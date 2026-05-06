import base64
import bcrypt
import hashlib
import hmac
import json
import threading
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from fastapi import Header

from app.core.config import settings

_REVOKED_TOKENS = {}
_REVOKED_TOKENS_LOCK = threading.Lock()


def _legacy_hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False

    if password_hash.startswith("$2"):
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
        except ValueError:
            return False

    return hmac.compare_digest(_legacy_hash_password(password), password_hash)


def password_needs_rehash(password_hash: str) -> bool:
    return not str(password_hash or "").startswith("$2")


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _split_token(token: str) -> Optional[tuple[str, str, str]]:
    parts = token.split(".", 2)
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


def _verify_signature(header_segment: str, payload_segment: str, signature_segment: str) -> bool:
    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    expected_signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    return hmac.compare_digest(_b64_encode(expected_signature), signature_segment)


def _decode_payload(token: str) -> Optional[dict]:
    parts = _split_token(token)
    if not parts:
        return None

    header_segment, payload_segment, signature_segment = parts
    if not _verify_signature(header_segment, payload_segment, signature_segment):
        return None

    try:
        payload = json.loads(_b64_decode(payload_segment).decode("utf-8"))
        return payload if isinstance(payload, dict) else None
    except (ValueError, json.JSONDecodeError):
        return None


def _prune_revoked_tokens(now_ts: Optional[int] = None) -> None:
    current_ts = now_ts or int(datetime.now(timezone.utc).timestamp())
    expired_tokens = [
        token for token, exp in _REVOKED_TOKENS.items() if int(exp) <= current_ts
    ]
    for token in expired_tokens:
        _REVOKED_TOKENS.pop(token, None)


def revoke_access_token(token: Optional[str]) -> bool:
    if not token:
        return False

    payload = _decode_payload(token)
    if not payload:
        return False

    try:
        exp = int(payload["exp"])
    except (KeyError, TypeError, ValueError):
        return False

    with _REVOKED_TOKENS_LOCK:
        _prune_revoked_tokens()
        _REVOKED_TOKENS[token] = exp

    return True


def _is_token_revoked(token: str) -> bool:
    with _REVOKED_TOKENS_LOCK:
        _prune_revoked_tokens()
        return token in _REVOKED_TOKENS


def create_access_token(user_id: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    expire_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "exp": int(expire_at.timestamp()),
        "jti": uuid4().hex,
    }
    header_segment = _b64_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    payload_segment = _b64_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    return f"{header_segment}.{payload_segment}.{_b64_encode(signature)}"


def decode_access_token(token: str) -> Optional[int]:
    if _is_token_revoked(token):
        return None

    payload = _decode_payload(token)
    if not payload:
        return None
    try:
        if int(payload["exp"]) < int(datetime.now(timezone.utc).timestamp()):
            return None
        return int(payload["sub"])
    except (KeyError, ValueError):
        return None


def get_bearer_token(authorization: Optional[str] = Header(default=None)) -> Optional[str]:
    if not authorization:
        return None
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None
    return authorization[len(prefix) :].strip()
