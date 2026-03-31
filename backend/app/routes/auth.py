from fastapi import APIRouter

from app.core.responses import error, success
from app.schemas import LoginRequest, RegisterRequest
from app.services import api_service

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register")
def register_user(payload: RegisterRequest):
    data, err = api_service.register_user(payload.username, payload.email, payload.password)
    if err:
        return error(err[0], err[1], err[2])
    return success(data, status_code=201)


@router.post("/login")
def login_user(payload: LoginRequest):
    data, err = api_service.login_user(payload.email, payload.password)
    if err:
        return error(err[0], err[1], err[2])
    return success(data)


@router.post("/logout")
def logout_user():
    return success(api_service.logout_user())
