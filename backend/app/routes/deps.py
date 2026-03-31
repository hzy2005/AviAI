from typing import Optional

from fastapi import Depends

from app.core.auth import get_bearer_token
from app.services.api_service import resolve_user_from_token


def get_current_user(token: Optional[str] = Depends(get_bearer_token)):
    return resolve_user_from_token(token)
