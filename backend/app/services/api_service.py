from datetime import datetime, timezone
from typing import Optional

from app.core.auth import create_access_token, decode_access_token, hash_password, verify_password
from app.mock_data import STORE, paginate


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_user_by_id(user_id: int):
    return next((user for user in STORE["users"] if user["id"] == user_id), None)


def find_user_by_email(email: str):
    return next((user for user in STORE["users"] if user["email"] == email), None)


def find_post(post_id: int):
    return next((post for post in STORE["posts"] if post["postId"] == post_id), None)


def serialize_user_brief(user: dict):
    return {
        "id": user["id"],
        "username": user["username"],
        "avatarUrl": user["avatarUrl"],
    }


def resolve_user_from_token(token: Optional[str]):
    if not token:
        return None
    user_id = decode_access_token(token)
    if not user_id:
        return None
    return find_user_by_id(user_id)


def register_user(username: str, email: str, password: str):
    if find_user_by_email(email):
        return None, (1009, "邮箱已注册", 409)

    if any(user["username"] == username for user in STORE["users"]):
        return None, (1009, "用户名已存在", 409)

    user = {
        "id": STORE["next_user_id"],
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "avatarUrl": "",
        "createdAt": now_iso(),
    }
    STORE["next_user_id"] += 1
    STORE["users"].append(user)
    return {"userId": user["id"]}, None


def login_user(email: str, password: str):
    user = find_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return None, (1002, "邮箱或密码错误", 401)

    return {
        "token": create_access_token(user["id"]),
        "user": serialize_user_brief(user),
    }, None


def logout_user():
    return {"success": True}


def get_user_profile(current_user: Optional[dict]):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "avatarUrl": current_user["avatarUrl"],
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

    record = {
        "recordId": STORE["next_record_id"],
        "userId": current_user["id"],
        "birdName": bird_name,
        "confidence": confidence,
        "imageUrl": "/uploads/{0}".format(filename),
        "createdAt": now_iso(),
    }
    STORE["next_record_id"] += 1
    STORE["bird_records"].insert(0, record)

    return {
        "recordId": record["recordId"],
        "birdName": record["birdName"],
        "confidence": record["confidence"],
        "imageUrl": record["imageUrl"],
        "createdAt": record["createdAt"],
    }, None


def list_bird_records(current_user: Optional[dict], page: int, page_size: int):
    if not current_user:
        return None, (1002, "未登录或 Token 无效", 401)

    items = [
        {
            "recordId": record["recordId"],
            "birdName": record["birdName"],
            "confidence": record["confidence"],
            "imageUrl": record["imageUrl"],
            "createdAt": record["createdAt"],
        }
        for record in STORE["bird_records"]
        if record["userId"] == current_user["id"]
    ]
    return paginate(items, page, page_size), None


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

    if current_user["id"] not in post["likeUserIds"]:
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
