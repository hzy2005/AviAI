from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import create_access_token, decode_access_token, hash_password, verify_password
from app.db.session import SessionLocal
from app.mock_data import STORE, paginate
from app.models.bird_record import BirdRecord
from app.models.user import User


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dt_to_iso(value: Optional[datetime]) -> str:
    if not value:
        return now_iso()
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc).isoformat()
    return value.astimezone(timezone.utc).isoformat()


def _serialize_user_model(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "password_hash": user.password_hash,
        "avatarUrl": user.avatar_url or "",
        "createdAt": _dt_to_iso(user.created_at),
    }


def find_user_by_id(user_id: int):
    # Keep compatibility for mock-backed posts data.
    mock_user = next((user for user in STORE["users"] if user["id"] == user_id), None)
    if mock_user:
        return mock_user

    try:
        with SessionLocal() as db:
            user = db.get(User, user_id)
            if not user:
                return None
            return _serialize_user_model(user)
    except SQLAlchemyError:
        return None


def find_user_by_email(email: str):
    try:
        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.email == email))
            if not user:
                return None
            return _serialize_user_model(user)
    except SQLAlchemyError:
        return None


def find_post(post_id: int):
    return next((post for post in STORE["posts"] if post["postId"] == post_id), None)


def serialize_user_brief(user: dict):
    return {
        "id": user["id"],
        "username": user["username"],
        "avatarUrl": user.get("avatarUrl", "") or "",
    }


def resolve_user_from_token(token: Optional[str]):
    if not token:
        return None
    user_id = decode_access_token(token)
    if not user_id:
        return None
    return find_user_by_id(user_id)


def register_user(username: str, email: str, password: str):
    try:
        with SessionLocal() as db:
            if db.scalar(select(User).where(User.email == email)):
                return None, (1009, "邮箱已注册", 409)
            if db.scalar(select(User).where(User.username == username)):
                return None, (1009, "用户名已存在", 409)

            user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                avatar_url="",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return {"userId": user.id}, None
    except SQLAlchemyError:
        return None, (1005, "服务内部错误", 500)


def login_user(email: str, password: str):
    try:
        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.email == email))
            if not user or not verify_password(password, user.password_hash):
                return None, (1002, "邮箱或密码错误", 401)

            user_dict = _serialize_user_model(user)
            return {
                "token": create_access_token(user_dict["id"]),
                "user": serialize_user_brief(user_dict),
            }, None
    except SQLAlchemyError:
        return None, (1005, "服务内部错误", 500)


def logout_user():
    return {"success": True}


def get_user_profile(current_user: Optional[dict]):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "avatarUrl": current_user.get("avatarUrl", "") or "",
        "createdAt": current_user["createdAt"],
    }, None


def recognize_bird_for_user(current_user: Optional[dict], filename: Optional[str]):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)
    if not filename:
        return None, (1006, "上传文件不合法", 400)

    lowered_name = filename.lower()
    if not lowered_name.endswith((".jpg", ".jpeg", ".png")):
        return None, (1006, "上传文件不合法", 400)

    bird_name = "白鹭"
    confidence = 0.9342
    if "king" in lowered_name or "cui" in lowered_name:
        bird_name = "翠鸟"
        confidence = 0.8911

    try:
        with SessionLocal() as db:
            record = BirdRecord(
                user_id=current_user["id"],
                bird_name=bird_name,
                confidence=confidence,
                image_url=f"/uploads/{filename}",
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            return {
                "recordId": record.id,
                "birdName": record.bird_name,
                "confidence": float(record.confidence),
                "imageUrl": record.image_url,
                "createdAt": _dt_to_iso(record.created_at),
            }, None
    except SQLAlchemyError:
        return None, (1005, "服务内部错误", 500)


def list_bird_records(current_user: Optional[dict], page: int, page_size: int):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    try:
        with SessionLocal() as db:
            total = db.scalar(
                select(func.count(BirdRecord.id)).where(
                    BirdRecord.user_id == current_user["id"]
                )
            ) or 0
            records = db.scalars(
                select(BirdRecord)
                .where(BirdRecord.user_id == current_user["id"])
                .order_by(BirdRecord.created_at.desc(), BirdRecord.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()

            return {
                "list": [
                    {
                        "recordId": record.id,
                        "birdName": record.bird_name,
                        "confidence": float(record.confidence),
                        "imageUrl": record.image_url,
                        "createdAt": _dt_to_iso(record.created_at),
                    }
                    for record in records
                ],
                "total": int(total),
                "page": page,
                "pageSize": page_size,
            }, None
    except SQLAlchemyError:
        return None, (1005, "服务内部错误", 500)


def create_post(current_user: Optional[dict], content: str, image_url: Optional[str]):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    post = {
        "postId": STORE["next_post_id"],
        "userId": current_user["id"],
        "content": content,
        "imageUrl": image_url,
        "likeUserIds": [],
        "commentCount": 0,
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    STORE["next_post_id"] += 1
    STORE["posts"].insert(0, post)
    return {"postId": post["postId"]}, None


def build_post_item(post: dict):
    user = find_user_by_id(post["userId"])
    if not user:
        return None
    return {
        "postId": post["postId"],
        "content": post["content"],
        "imageUrl": post["imageUrl"],
        "likeCount": len(post["likeUserIds"]),
        "commentCount": post["commentCount"],
        "createdAt": post["createdAt"],
        "updatedAt": post.get("updatedAt", post["createdAt"]),
        "author": serialize_user_brief(user),
    }


def list_posts(page: int, page_size: int, keyword: Optional[str] = None):
    items = []
    normalized_keyword = (keyword or "").strip().lower()
    for post in STORE["posts"]:
        if normalized_keyword and normalized_keyword not in post["content"].lower():
            continue
        post_item = build_post_item(post)
        if post_item:
            items.append(post_item)
    return paginate(items, page, page_size), None


def get_post_detail(post_id: int):
    post = find_post(post_id)
    if not post:
        return None, (1004, "资源不存在", 404)
    return build_post_item(post), None


def update_post(current_user: Optional[dict], post_id: int, content: str, image_url: Optional[str]):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    post = find_post(post_id)
    if not post:
        return None, (1004, "资源不存在", 404)
    if post["userId"] != current_user["id"]:
        return None, (1003, "无权限", 403)

    post["content"] = content
    post["imageUrl"] = image_url
    post["updatedAt"] = now_iso()
    return {"postId": post_id}, None


def delete_post(current_user: Optional[dict], post_id: int):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    post = find_post(post_id)
    if not post:
        return None, (1004, "资源不存在", 404)
    if post["userId"] != current_user["id"]:
        return None, (1003, "无权限", 403)

    STORE["posts"] = [item for item in STORE["posts"] if item["postId"] != post_id]
    STORE["comments"] = [item for item in STORE["comments"] if item["postId"] != post_id]
    return {"postId": post_id, "deleted": True}, None


def like_post(current_user: Optional[dict], post_id: int):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    post = find_post(post_id)
    if not post:
        return None, (1004, "资源不存在", 404)

    if current_user["id"] in post["likeUserIds"]:
        return None, (1009, "资源冲突", 409)

    post["likeUserIds"].append(current_user["id"])
    return {"postId": post_id, "liked": True}, None


def create_comment(current_user: Optional[dict], post_id: int, content: str, parent_id: Optional[int]):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    post = find_post(post_id)
    if not post:
        return None, (1004, "资源不存在", 404)

    if parent_id is not None and not any(
        comment["commentId"] == parent_id for comment in STORE["comments"]
    ):
        return None, (1004, "父评论不存在", 404)

    comment = {
        "commentId": STORE["next_comment_id"],
        "postId": post_id,
        "userId": current_user["id"],
        "content": content,
        "parentId": parent_id,
        "createdAt": now_iso(),
    }
    STORE["next_comment_id"] += 1
    STORE["comments"].append(comment)
    post["commentCount"] += 1
    post["updatedAt"] = now_iso()
    return {"commentId": comment["commentId"]}, None
