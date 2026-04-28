from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services import api_service


def _session_factory(db):
    session_context = MagicMock()
    session_context.__enter__.return_value = db
    session_context.__exit__.return_value = False
    return MagicMock(return_value=session_context)


def test_register_user_returns_conflict_when_email_exists():
    db = MagicMock()
    db.scalar.return_value = SimpleNamespace(id=1)

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        data, err = api_service.register_user("alice", "alice@example.com", "12345678")

    assert data is None
    assert err == (1009, "Email already registered", 409)
    db.scalar.assert_called_once()
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_register_user_returns_conflict_when_username_exists():
    db = MagicMock()
    db.scalar.side_effect = [None, SimpleNamespace(id=2)]

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        data, err = api_service.register_user("alice", "alice@example.com", "12345678")

    assert data is None
    assert err == (1009, "Username already registered", 409)
    assert db.scalar.call_count == 2
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_register_user_commits_new_user_and_returns_id():
    db = MagicMock()
    db.scalar.side_effect = [None, None]

    def assign_id(user):
        user.id = 42

    db.refresh.side_effect = assign_id

    with patch.object(api_service, "SessionLocal", _session_factory(db)), patch.object(
        api_service, "hash_password", return_value="hashed-password"
    ) as mock_hash:
        data, err = api_service.register_user("alice", "alice@example.com", "12345678")

    assert err is None
    assert data == {"userId": 42}
    mock_hash.assert_called_once_with("12345678")
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


def test_login_user_returns_unauthorized_when_user_missing():
    db = MagicMock()
    db.scalar.return_value = None

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        data, err = api_service.login_user("missing@example.com", "12345678")

    assert data is None
    assert err == (1002, "Invalid email or password", 401)
    db.scalar.assert_called_once()


def test_login_user_returns_unauthorized_when_password_wrong():
    db = MagicMock()
    db.scalar.return_value = SimpleNamespace(password_hash="stored-hash")

    with patch.object(api_service, "SessionLocal", _session_factory(db)), patch.object(
        api_service, "verify_password", return_value=False
    ) as mock_verify:
        data, err = api_service.login_user("alice@example.com", "wrong-password")

    assert data is None
    assert err == (1002, "Invalid email or password", 401)
    mock_verify.assert_called_once_with("wrong-password", "stored-hash")


def test_resolve_user_from_token_returns_none_without_token():
    with patch.object(api_service, "decode_access_token") as mock_decode:
        assert api_service.resolve_user_from_token(None) is None

    mock_decode.assert_not_called()


def test_resolve_user_from_token_returns_none_when_token_invalid():
    with patch.object(api_service, "decode_access_token", return_value=None) as mock_decode, patch.object(
        api_service, "find_user_by_id"
    ) as mock_find_user:
        assert api_service.resolve_user_from_token("bad-token") is None

    mock_decode.assert_called_once_with("bad-token")
    mock_find_user.assert_not_called()


def test_upload_post_image_returns_unauthorized_without_user():
    data, err = api_service.upload_post_image(None, "bird.jpg", b"image-bytes")

    assert data is None
    assert err == (1002, "Unauthorized", 401)


def test_upload_post_image_rejects_invalid_extension(fake_user):
    with patch.object(api_service, "_save_upload_file") as mock_save:
        data, err = api_service.upload_post_image(fake_user, "bird.gif", b"image-bytes")

    assert data is None
    assert err == (1006, "Invalid upload file.", 400)
    mock_save.assert_not_called()


def test_upload_post_image_saves_allowed_image(fake_user):
    with patch.object(api_service, "_save_upload_file", return_value="/uploads/bird.jpg") as mock_save:
        data, err = api_service.upload_post_image(fake_user, "bird.jpg", b"image-bytes")

    assert err is None
    assert data == {"imageUrl": "/uploads/bird.jpg"}
    mock_save.assert_called_once_with("bird.jpg", b"image-bytes")


def test_generate_post_copywriting_rejects_invalid_mode(fake_user):
    with patch.object(api_service, "_call_deepseek_chat") as mock_chat, patch.object(
        api_service, "_call_deepseek_vision_chat"
    ) as mock_vision:
        data, err = api_service.generate_post_copywriting(
            current_user=fake_user,
            mode="rewrite",
            image_url="/uploads/bird.jpg",
            content="",
        )

    assert data is None
    assert err == (1001, "Invalid mode. Use generate or polish.", 400)
    mock_chat.assert_not_called()
    mock_vision.assert_not_called()


def test_generate_post_copywriting_requires_content_for_polish(fake_user):
    with patch.object(api_service, "_call_deepseek_chat") as mock_chat, patch.object(
        api_service, "_call_deepseek_vision_chat"
    ) as mock_vision:
        data, err = api_service.generate_post_copywriting(
            current_user=fake_user,
            mode="polish",
            image_url="/uploads/bird.jpg",
            content="",
        )

    assert data is None
    assert err == (1001, "content is required when mode is polish.", 400)
    mock_chat.assert_not_called()
    mock_vision.assert_not_called()


def test_generate_post_copywriting_uses_fallback_when_ai_quality_fails(fake_user):
    quality_failure = {
        "content": None,
        "attempts": 2,
        "retryCount": 1,
        "fallback": True,
        "elapsedMs": 25,
    }

    with patch.object(api_service, "_is_backend_accessible_image", return_value=True), patch.object(
        api_service,
        "_resolve_bird_hint_for_copywriting",
        return_value={"birdName": "Mallard", "confidence": 0.91},
    ), patch.object(api_service, "_extract_vision_facts", return_value=None), patch.object(
        api_service, "_build_visual_grounding_hint", return_value="water_surface"
    ), patch.object(
        api_service, "_call_with_quality_retry_meta", return_value=quality_failure
    ) as mock_retry:
        data, err = api_service.generate_post_copywriting(
            current_user=fake_user,
            mode="generate",
            image_url="/uploads/bird.jpg",
            content="",
        )

    assert err is None
    assert data["mode"] == "generate"
    assert data["source"] == "fallback"
    assert data["content"]
    assert data["aiMeta"]["fallback"] is True
    assert data["aiMeta"]["retryCount"] == 1
    mock_retry.assert_called_once()


def test_like_post_returns_conflict_when_user_already_liked(fake_user):
    db = MagicMock()
    db.get.return_value = SimpleNamespace(id=10, like_count=1)
    db.scalar.return_value = SimpleNamespace(id=99)

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        data, err = api_service.like_post(fake_user, post_id=10)

    assert data is None
    assert err[0] == 1009
    assert err[2] == 409
    db.get.assert_called_once()
    db.scalar.assert_called_once()
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_like_post_creates_like_when_not_existing(fake_user):
    post = SimpleNamespace(id=10, like_count=0, updated_at=None)
    db = MagicMock()
    db.get.return_value = post
    db.scalar.return_value = None

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        data, err = api_service.like_post(fake_user, post_id=10)

    assert err is None
    assert data == {"postId": 10, "liked": True}
    assert post.like_count == 1
    assert post.updated_at is not None
    db.add.assert_called_once()
    db.commit.assert_called_once()
