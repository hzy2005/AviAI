from fastapi import APIRouter, Depends

from app.core.responses import error, success
from app.routes.deps import get_current_user
from app.services import api_service

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me")
def get_current_user_profile(current_user=Depends(get_current_user)):
    data, err = api_service.get_user_profile(current_user)
    if err:
        return error(err[0], err[1], err[2])
    return success(data)
