from fastapi import APIRouter, Depends, File, Query, UploadFile

from app.core.responses import error, success
from app.routes.deps import get_current_user
from app.schemas import AICopywritingRequest, CreateCommentRequest, CreatePostRequest
from app.services import api_service

router = APIRouter(prefix="/api/v1/posts", tags=["Posts"])


@router.post("")
def create_post(payload: CreatePostRequest, current_user=Depends(get_current_user)):
    data, err = api_service.create_post(current_user, payload.content, payload.imageUrl)
    if err:
        return error(err[0], err[1], err[2])
    return success(data, status_code=201)


@router.post("/ai-copywriting")
def ai_copywriting(payload: AICopywritingRequest, current_user=Depends(get_current_user)):
    data, err = api_service.generate_post_copywriting(
        current_user=current_user,
        mode=payload.mode,
        image_url=payload.imageUrl,
        content=payload.content,
    )
    if err:
        return error(err[0], err[1], err[2])
    return success(data)


@router.post("/upload-image")
async def upload_post_image(
    image: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    file_bytes = await image.read()
    data, err = api_service.upload_post_image(current_user, image.filename, file_bytes)
    if err:
        return error(err[0], err[1], err[2])
    return success(data, status_code=201)


@router.get("")
def list_posts(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
):
    data, _ = api_service.list_posts(page, pageSize, keyword)
    return success(data)


@router.get("/{post_id}")
def get_post_detail(post_id: int):
    data, err = api_service.get_post_detail(post_id)
    if err:
        return error(err[0], err[1], err[2])
    return success(data)


@router.put("/{post_id}")
def update_post(post_id: int, payload: CreatePostRequest, current_user=Depends(get_current_user)):
    data, err = api_service.update_post(current_user, post_id, payload.content, payload.imageUrl)
    if err:
        return error(err[0], err[1], err[2])
    return success(data)


@router.delete("/{post_id}")
def delete_post(post_id: int, current_user=Depends(get_current_user)):
    data, err = api_service.delete_post(current_user, post_id)
    if err:
        return error(err[0], err[1], err[2])
    return success(data)


@router.post("/{post_id}/like")
def like_post(post_id: int, current_user=Depends(get_current_user)):
    data, err = api_service.like_post(current_user, post_id)
    if err:
        return error(err[0], err[1], err[2])
    return success(data)


@router.post("/{post_id}/comments")
def create_post_comment(
    post_id: int,
    payload: CreateCommentRequest,
    current_user=Depends(get_current_user),
):
    data, err = api_service.create_comment(
        current_user, post_id, payload.content, payload.parentId
    )
    if err:
        return error(err[0], err[1], err[2])
    return success(data, status_code=201)
