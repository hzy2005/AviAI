from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.auth import create_access_token, decode_access_token, hash_password, verify_password
from app.db.session import SessionLocal
from app.models.bird_record import BirdRecord
from app.models.comment import Comment
from app.models.like import Like
from app.models.post import Post
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


def _serialize_post_item(post: Post, author: dict) -> dict:
    return {
        "postId": post.id,
        "content": post.content,
        "imageUrl": post.image_url,
        "likeCount": int(post.like_count or 0),
        "commentCount": int(post.comment_count or 0),
        "createdAt": _dt_to_iso(post.created_at),
        "updatedAt": _dt_to_iso(post.updated_at),
        "author": {
            "id": author["id"],
            "username": author["username"],
            "avatarUrl": author.get("avatarUrl", "") or "",
        },
    }


def find_user_by_id(user_id: int):
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

    try:
        with SessionLocal() as db:
            post = Post(
                user_id=current_user["id"],
                content=content,
                image_url=image_url,
                like_count=0,
                comment_count=0,
            )
            db.add(post)
            db.commit()
            db.refresh(post)
            return {"postId": post.id}, None
    except SQLAlchemyError:
        return None, (1005, "服务内部错误", 500)


def list_posts(page: int, page_size: int, keyword: Optional[str] = None):
    normalized_keyword = (keyword or "").strip()

    try:
        with SessionLocal() as db:
            query = select(Post)
            count_query = select(func.count(Post.id))
            if normalized_keyword:
                like_keyword = f"%{normalized_keyword}%"
                query = query.where(Post.content.ilike(like_keyword))
                count_query = count_query.where(Post.content.ilike(like_keyword))

            total = db.scalar(count_query) or 0
            posts = db.scalars(
                query
                .order_by(Post.created_at.desc(), Post.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()

            user_ids = [post.user_id for post in posts]
            users = db.scalars(select(User).where(User.id.in_(user_ids))).all() if user_ids else []
            users_map = {user.id: _serialize_user_model(user) for user in users}

            items = []
            for post in posts:
                author = users_map.get(post.user_id)
                if not author:
                    continue
                items.append(_serialize_post_item(post, author))

            return {
                "list": items,
                "total": int(total),
                "page": page,
                "pageSize": page_size,
            }, None
    except SQLAlchemyError:
        return None, (1005, "服务内部错误", 500)


def get_post_detail(post_id: int):
    try:
        with SessionLocal() as db:
            post = db.get(Post, post_id)
            if not post:
                return None, (1004, "资源不存在", 404)

            user = db.get(User, post.user_id)
            if not user:
                return None, (1004, "资源不存在", 404)

            return _serialize_post_item(post, _serialize_user_model(user)), None
    except SQLAlchemyError:
        return None, (1005, "服务内部错误", 500)


def update_post(current_user: Optional[dict], post_id: int, content: str, image_url: Optional[str]):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    try:
        with SessionLocal() as db:
            post = db.get(Post, post_id)
            if not post:
                return None, (1004, "资源不存在", 404)
            if post.user_id != current_user["id"]:
                return None, (1003, "无权限", 403)

            post.content = content
            post.image_url = image_url
            post.updated_at = datetime.now(timezone.utc)
            db.commit()
            return {"postId": post_id}, None
    except SQLAlchemyError:
        return None, (1005, "服务内部错误", 500)


def delete_post(current_user: Optional[dict], post_id: int):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    try:
        with SessionLocal() as db:
            post = db.get(Post, post_id)
            if not post:
                return None, (1004, "资源不存在", 404)
            if post.user_id != current_user["id"]:
                return None, (1003, "无权限", 403)

            db.delete(post)
            db.commit()
            return {"postId": post_id, "deleted": True}, None
    except SQLAlchemyError:
        return None, (1005, "服务内部错误", 500)


def like_post(current_user: Optional[dict], post_id: int):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    try:
        with SessionLocal() as db:
            post = db.get(Post, post_id)
            if not post:
                return None, (1004, "资源不存在", 404)

            existing = db.scalar(
                select(Like).where(
                    Like.post_id == post_id,
                    Like.user_id == current_user["id"],
                )
            )
            if existing:
                return None, (1009, "资源冲突", 409)

            like = Like(user_id=current_user["id"], post_id=post_id)
            db.add(like)
            post.like_count = int(post.like_count or 0) + 1
            post.updated_at = datetime.now(timezone.utc)
            db.commit()
            return {"postId": post_id, "liked": True}, None
    except IntegrityError:
        return None, (1009, "资源冲突", 409)
    except SQLAlchemyError:
        return None, (1005, "服务内部错误", 500)


def create_comment(current_user: Optional[dict], post_id: int, content: str, parent_id: Optional[int]):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    try:
        with SessionLocal() as db:
            post = db.get(Post, post_id)
            if not post:
                return None, (1004, "资源不存在", 404)

            if parent_id is not None:
                parent_comment = db.get(Comment, parent_id)
                if not parent_comment or parent_comment.post_id != post_id:
                    return None, (1004, "父评论不存在", 404)

            comment = Comment(
                post_id=post_id,
                user_id=current_user["id"],
                content=content,
                parent_id=parent_id,
            )
            db.add(comment)
            post.comment_count = int(post.comment_count or 0) + 1
            post.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(comment)
            return {"commentId": comment.id}, None
    except SQLAlchemyError:
        return None, (1005, "服务内部错误", 500)
