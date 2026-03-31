from fastapi import APIRouter, Depends, File, Query, UploadFile

from app.core.responses import error, success
from app.routes.deps import get_current_user
from app.services import api_service

router = APIRouter(prefix="/api/v1/birds", tags=["Birds"])


@router.post("/recognize")
async def recognize_bird(
    image: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    data, err = api_service.recognize_bird_for_user(current_user, image.filename)
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
