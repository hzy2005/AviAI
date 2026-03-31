from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from app.core.auth import hash_password


def _now_offset(minutes: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat()


def create_seed_data():
    users = [
        {
            "id": 1,
            "username": "birdlover",
            "email": "bird@example.com",
            "password_hash": hash_password("12345678"),
            "avatarUrl": "",
            "createdAt": _now_offset(5000),
        }
    ]

    bird_records = [
        {
            "recordId": 101,
            "userId": 1,
            "birdName": "白鹭",
            "confidence": 0.9342,
            "imageUrl": "/uploads/20260309_egret.jpg",
            "createdAt": _now_offset(180),
        },
        {
            "recordId": 102,
            "userId": 1,
            "birdName": "翠鸟",
            "confidence": 0.8911,
            "imageUrl": "/uploads/20260310_kingfisher.jpg",
            "createdAt": _now_offset(60),
        },
    ]

    posts = [
        {
            "postId": 1001,
            "userId": 1,
            "content": "今天在湿地拍到了白鹭！",
            "imageUrl": "/uploads/post_001.jpg",
            "likeUserIds": [1],
            "commentCount": 1,
            "createdAt": _now_offset(240),
        }
    ]

    comments = [
        {
            "commentId": 501,
            "postId": 1001,
            "userId": 1,
            "content": "拍得很清晰！",
            "parentId": None,
            "createdAt": _now_offset(230),
        }
    ]

    return {
        "users": users,
        "bird_records": bird_records,
        "posts": posts,
        "comments": comments,
        "next_user_id": 2,
        "next_record_id": 103,
        "next_post_id": 1002,
        "next_comment_id": 502,
    }


STORE = create_seed_data()


def reset_store():
    global STORE
    STORE = create_seed_data()


def paginate(items: List[Dict], page: int, page_size: int):
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "list": deepcopy(items[start:end]),
        "total": len(items),
        "page": page,
        "pageSize": page_size,
    }
