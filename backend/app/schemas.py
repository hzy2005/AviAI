from typing import Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=64)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=64)


class CreatePostRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1000)
    imageUrl: Optional[str] = None


class CreateCommentRequest(BaseModel):
    content: str = Field(min_length=1, max_length=500)
    parentId: Optional[int] = None
