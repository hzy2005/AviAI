import base64
import hashlib
import hmac
import json
import logging
import time

import pytest

from app.core import auth
from app.core.responses import error, success
from app.schemas import AICopywritingRequest, CreatePostRequest, LoginRequest
from app.utils.logger import JsonFormatter


def test_access_token_round_trip_decodes_user_id():
    token = auth.create_access_token(123)

    assert auth.decode_access_token(token) == 123


def test_decode_access_token_rejects_tampered_signature():
    token = auth.create_access_token(123)
    header, payload, _signature = token.split(".")

    tampered = f"{header}.{payload}.invalid-signature"

    assert auth.decode_access_token(tampered) is None


def test_decode_access_token_rejects_expired_payload():
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": "123", "exp": int(time.time()) - 10}

    header_segment = auth._b64_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = auth._b64_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    signature = hmac.new(auth.settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    token = f"{header_segment}.{payload_segment}.{auth._b64_encode(signature)}"

    assert auth.decode_access_token(token) is None


def test_decode_access_token_rejects_malformed_token():
    assert auth.decode_access_token("not-a-jwt") is None


def test_get_bearer_token_extracts_authorization_value():
    assert auth.get_bearer_token("Bearer abc123") == "abc123"
    assert auth.get_bearer_token("Token abc123") is None
    assert auth.get_bearer_token(None) is None


def test_password_hash_and_verify_password():
    hashed = auth.hash_password("secret")

    assert hashed.startswith("$2")
    assert auth.verify_password("secret", hashed) is True
    assert auth.verify_password("wrong", hashed) is False


def test_password_verify_accepts_legacy_sha256_hash():
    legacy_hash = hashlib.sha256("secret".encode("utf-8")).hexdigest()

    assert auth.verify_password("secret", legacy_hash) is True
    assert auth.password_needs_rehash(legacy_hash) is True


def test_revoked_token_can_no_longer_be_decoded():
    token = auth.create_access_token(123)

    assert auth.revoke_access_token(token) is True
    assert auth.decode_access_token(token) is None


def test_b64_decode_accepts_unpadded_data():
    raw = b"hello"
    encoded = base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

    assert auth._b64_decode(encoded) == raw


def test_success_response_uses_unified_envelope():
    response = success({"ok": True})

    assert response.status_code == 200
    body = json.loads(response.body)
    assert body == {"code": 0, "msg": "success", "message": "success", "data": {"ok": True}}


def test_error_response_uses_unified_envelope():
    response = error(1001, "bad request", 400, data={"field": "email"})

    assert response.status_code == 400
    body = json.loads(response.body)
    assert body == {
        "code": 1001,
        "msg": "bad request",
        "message": "bad request",
        "data": {"field": "email"},
    }


def test_json_formatter_outputs_structured_log_fields():
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request completed",
        args=(),
        exc_info=None,
    )
    record.method = "GET"
    record.path = "/health"
    record.status_code = 200
    record.duration_ms = 12.34

    body = json.loads(JsonFormatter().format(record))

    assert body["level"] == "INFO"
    assert body["message"] == "request completed"
    assert body["module"] == "test_core_modules"
    assert body["method"] == "GET"
    assert body["path"] == "/health"
    assert body["status_code"] == 200
    assert body["duration_ms"] == 12.34


def test_json_formatter_structures_uvicorn_access_log_fields():
    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='%s - "%s %s HTTP/%s" %d',
        args=("127.0.0.1:51234", "GET", "/health", "1.1", 200),
        exc_info=None,
    )

    body = json.loads(JsonFormatter().format(record))

    assert body["logger"] == "uvicorn.access"
    assert body["client"] == "127.0.0.1:51234"
    assert body["method"] == "GET"
    assert body["path"] == "/health"
    assert body["status_code"] == 200


def test_login_request_requires_valid_lengths():
    assert LoginRequest(email="valid@example.com", password="12345678").email == "valid@example.com"

    with pytest.raises(Exception):
        LoginRequest(email="", password="short")


def test_create_post_request_requires_content():
    assert CreatePostRequest(content="hello", imageUrl=None).content == "hello"

    with pytest.raises(Exception):
        CreatePostRequest(content="", imageUrl=None)


def test_ai_copywriting_request_restricts_mode():
    assert AICopywritingRequest(mode="generate", imageUrl="/uploads/a.jpg").mode == "generate"

    with pytest.raises(Exception):
        AICopywritingRequest(mode="rewrite", imageUrl="/uploads/a.jpg")
