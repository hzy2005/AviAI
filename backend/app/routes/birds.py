from fastapi import APIRouter, Depends, File, Query, UploadFile

from app.core.responses import error, success
from app.routes.deps import get_current_user
from app.schemas import UpdateBirdRecordRequest
from app.services import api_service

router = APIRouter(prefix="/api/v1/birds", tags=["Birds"])


@router.post("/recognize")
async def recognize_bird(
    image: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    file_bytes = await image.read()
    data, err = api_service.recognize_bird_for_user(
        current_user,
        image.filename,
        file_bytes,
    )
    if err:
        return error(err[0], err[1], err[2])
    return success(data, status_code=201)


@router.get("/records")
def list_bird_records(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    current_user=Depends(get_current_user),
):
    data, err = api_service.list_bird_records(current_user, page, pageSize)
    if err:
        return error(err[0], err[1], err[2])
    return success(data)


@router.get("/records/{record_id}")
def get_bird_record_detail(record_id: int, current_user=Depends(get_current_user)):
    data, err = api_service.get_bird_record_detail(current_user, record_id)
    if err:
        return error(err[0], err[1], err[2])
    return success(data)


@router.put("/records/{record_id}")
def update_bird_record(
    record_id: int,
    payload: UpdateBirdRecordRequest,
    current_user=Depends(get_current_user),
):
    data, err = api_service.update_bird_record(current_user, record_id, payload.birdName)
    if err:
        return error(err[0], err[1], err[2])
    return success(data)


@router.delete("/records/{record_id}")
def delete_bird_record(record_id: int, current_user=Depends(get_current_user)):
    data, err = api_service.delete_bird_record(current_user, record_id)
    if err:
        return error(err[0], err[1], err[2])
    return success(data)
