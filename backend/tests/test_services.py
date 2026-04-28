import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from PIL import Image
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.services import api_service


TEST_IMAGE_DIR = Path(__file__).resolve().parents[1] / "uploads" / "pytest-images"


def _session_factory(db):
    session_context = MagicMock()
    session_context.__enter__.return_value = db
    session_context.__exit__.return_value = False
    return MagicMock(return_value=session_context)


def _raising_session_factory(exc=None):
    session_context = MagicMock()
    session_context.__enter__.side_effect = exc or SQLAlchemyError("db down")
    session_context.__exit__.return_value = False
    return MagicMock(return_value=session_context)


class _FakeHTTPResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        if isinstance(self.payload, bytes):
            return self.payload
        return json.dumps(self.payload).encode("utf-8")


def _write_test_image(filename, color):
    TEST_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    image_path = TEST_IMAGE_DIR / filename
    Image.new("RGB", (8, 8), color).save(image_path)
    return image_path


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


def test_get_user_profile_returns_profile_for_current_user(fake_user):
    data, err = api_service.get_user_profile(fake_user)

    assert err is None
    assert data["id"] == fake_user["id"]
    assert data["email"] == fake_user["email"]


def test_get_user_profile_returns_unauthorized_without_user():
    data, err = api_service.get_user_profile(None)

    assert data is None
    assert err[0] == 1002
    assert err[2] == 401


def test_recognize_bird_rejects_missing_and_invalid_upload(fake_user):
    assert api_service.recognize_bird_for_user(None, "bird.jpg", b"x")[1][0] == 1002
    assert api_service.recognize_bird_for_user(fake_user, None, b"x")[1][0] == 1006
    assert api_service.recognize_bird_for_user(fake_user, "bird.jpg", b"")[1][0] == 1006
    assert api_service.recognize_bird_for_user(fake_user, "bird.gif", b"x")[1][0] == 1006


def test_list_bird_records_returns_paginated_items(fake_user):
    db = MagicMock()
    record = SimpleNamespace(
        id=7,
        bird_name="Mallard",
        confidence=0.9,
        image_url="/uploads/bird.jpg",
        created_at=None,
    )
    records_result = MagicMock()
    records_result.all.return_value = [record]
    db.scalar.return_value = 1
    db.scalars.return_value = records_result

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        data, err = api_service.list_bird_records(fake_user, page=1, page_size=10)

    assert err is None
    assert data["total"] == 1
    assert data["list"][0]["recordId"] == 7
    db.scalar.assert_called_once()
    db.scalars.assert_called_once()


def test_bird_record_detail_handles_not_found_forbidden_and_success(fake_user):
    db = MagicMock()

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        db.get.return_value = None
        data, err = api_service.get_bird_record_detail(fake_user, 1)
        assert data is None
        assert err[0] == 1004

        db.get.return_value = SimpleNamespace(user_id=999)
        data, err = api_service.get_bird_record_detail(fake_user, 1)
        assert data is None
        assert err[0] == 1003

        db.get.return_value = SimpleNamespace(
            id=1,
            user_id=fake_user["id"],
            bird_name="Mallard",
            confidence=0.8,
            image_url="/uploads/a.jpg",
            created_at=None,
        )
        data, err = api_service.get_bird_record_detail(fake_user, 1)

    assert err is None
    assert data["recordId"] == 1


def test_update_bird_record_updates_name_and_commits(fake_user):
    record = SimpleNamespace(
        id=2,
        user_id=fake_user["id"],
        bird_name="Old",
        confidence=0.7,
        image_url="/uploads/a.jpg",
        created_at=None,
    )
    db = MagicMock()
    db.get.return_value = record

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        data, err = api_service.update_bird_record(fake_user, 2, "  New Bird  ")

    assert err is None
    assert record.bird_name == "New Bird"
    assert data["birdName"] == "New Bird"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(record)


def test_delete_bird_record_deletes_owned_record(fake_user):
    record = SimpleNamespace(id=3, user_id=fake_user["id"])
    db = MagicMock()
    db.get.return_value = record

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        data, err = api_service.delete_bird_record(fake_user, 3)

    assert err is None
    assert data == {"recordId": 3, "deleted": True}
    db.delete.assert_called_once_with(record)
    db.commit.assert_called_once()


def test_create_post_creates_post_for_user(fake_user):
    db = MagicMock()

    def assign_id(post):
        post.id = 88

    db.refresh.side_effect = assign_id

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        data, err = api_service.create_post(fake_user, "hello", "/uploads/post.jpg")

    assert err is None
    assert data == {"postId": 88}
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_list_posts_returns_author_enriched_items():
    db = MagicMock()
    post = SimpleNamespace(
        id=5,
        user_id=1,
        content="bird story",
        image_url=None,
        like_count=2,
        comment_count=1,
        created_at=None,
        updated_at=None,
    )
    user = SimpleNamespace(
        id=1,
        username="tester",
        email="tester@example.com",
        password_hash="hash",
        avatar_url="",
        created_at=None,
    )
    posts_result = MagicMock()
    posts_result.all.return_value = [post]
    users_result = MagicMock()
    users_result.all.return_value = [user]
    db.scalar.return_value = 1
    db.scalars.side_effect = [posts_result, users_result]

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        data, err = api_service.list_posts(page=1, page_size=10, keyword="bird")

    assert err is None
    assert data["total"] == 1
    assert data["list"][0]["postId"] == 5
    assert data["list"][0]["author"]["username"] == "tester"


def test_get_post_detail_returns_not_found_or_detail():
    db = MagicMock()

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        db.get.return_value = None
        data, err = api_service.get_post_detail(404)
        assert data is None
        assert err[0] == 1004

        post = SimpleNamespace(
            id=5,
            user_id=1,
            content="bird story",
            image_url=None,
            like_count=0,
            comment_count=0,
            created_at=None,
            updated_at=None,
        )
        user = SimpleNamespace(
            id=1,
            username="tester",
            email="tester@example.com",
            password_hash="hash",
            avatar_url="",
            created_at=None,
        )
        db.get.side_effect = [post, user]
        data, err = api_service.get_post_detail(5)

    assert err is None
    assert data["postId"] == 5
    assert data["author"]["id"] == 1


def test_update_post_rejects_forbidden_and_updates_owner(fake_user):
    db = MagicMock()

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        db.get.return_value = SimpleNamespace(id=5, user_id=999)
        data, err = api_service.update_post(fake_user, 5, "new", None)
        assert data is None
        assert err[0] == 1003

        post = SimpleNamespace(id=5, user_id=fake_user["id"], content="old", image_url=None, updated_at=None)
        db.get.return_value = post
        data, err = api_service.update_post(fake_user, 5, "new", "/uploads/new.jpg")

    assert err is None
    assert data == {"postId": 5}
    assert post.content == "new"
    assert post.image_url == "/uploads/new.jpg"


def test_delete_post_deletes_owner_post(fake_user):
    post = SimpleNamespace(id=5, user_id=fake_user["id"])
    db = MagicMock()
    db.get.return_value = post

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        data, err = api_service.delete_post(fake_user, 5)

    assert err is None
    assert data == {"postId": 5, "deleted": True}
    db.delete.assert_called_once_with(post)
    db.commit.assert_called_once()


def test_create_comment_handles_parent_not_found_and_success(fake_user):
    db = MagicMock()
    post = SimpleNamespace(id=5, comment_count=0, updated_at=None)

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        db.get.side_effect = [post, None]
        data, err = api_service.create_comment(fake_user, 5, "hello", parent_id=99)
        assert data is None
        assert err[0] == 1004

        def assign_comment_id(comment):
            comment.id = 77

        db.get.side_effect = [post]
        db.refresh.side_effect = assign_comment_id
        data, err = api_service.create_comment(fake_user, 5, "hello", parent_id=None)

    assert err is None
    assert data == {"commentId": 77}
    assert post.comment_count == 1
    db.add.assert_called()
    db.commit.assert_called()


def test_copywriting_helper_functions_cover_quality_and_formatting():
    assert api_service._is_quality_passed("long enough content", 8, []) is True
    assert api_service._is_quality_passed("", 8, []) is False
    assert api_service._is_quality_passed("short", 20, []) is False
    assert api_service._is_quality_passed("bad template content", 8, ["template"]) is False

    facts = {
        "species": "mallard",
        "mainColor": "green",
        "location": "water_surface",
        "action": "swimming",
        "pose": "side",
    }
    formatted = api_service._format_vision_facts(facts)
    assert "species=mallard" in formatted
    assert api_service._format_vision_facts(None) == "unknown"
    assert api_service._humanize_bird_name("Mallard")
    assert api_service._extract_json_from_text("prefix {\"a\": 1} suffix") == {"a": 1}
    assert api_service._extract_json_from_text("no json") is None


def test_call_with_quality_retry_meta_retries_until_quality_passes():
    calls = iter(["bad", "this content is long enough"])

    result = api_service._call_with_quality_retry_meta(
        lambda: next(calls),
        min_length=10,
        banned_templates=[],
    )

    assert result["content"] == "this content is long enough"
    assert result["retryCount"] == 1
    assert result["fallback"] is False


def test_user_lookup_login_and_logout_cover_success_paths():
    user = SimpleNamespace(
        id=3,
        username="tester",
        email="tester@example.com",
        password_hash="stored-hash",
        avatar_url="/avatar.png",
        created_at=None,
    )

    db = MagicMock()
    db.get.return_value = user
    db.scalar.return_value = user

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        by_id = api_service.find_user_by_id(3)
        by_email = api_service.find_user_by_email("tester@example.com")

    assert by_id["id"] == 3
    assert by_email["email"] == "tester@example.com"
    assert api_service.serialize_user_brief(by_id) == {
        "id": 3,
        "username": "tester",
        "avatarUrl": "/avatar.png",
    }
    assert api_service.logout_user() == {"success": True}

    with patch.object(api_service, "SessionLocal", _session_factory(db)), patch.object(
        api_service, "verify_password", return_value=True
    ), patch.object(api_service, "create_access_token", return_value="token"):
        data, err = api_service.login_user("tester@example.com", "password")

    assert err is None
    assert data["token"] == "token"
    assert data["user"]["id"] == 3


def test_db_read_helpers_return_none_on_database_error():
    with patch.object(api_service, "SessionLocal", _raising_session_factory()):
        assert api_service.find_user_by_id(1) is None
        assert api_service.find_user_by_email("a@example.com") is None
        assert api_service._find_recent_bird_hint(1, "/uploads/a.jpg") is None


def test_local_image_resolution_and_visual_hint():
    image_path = _write_test_image("green.png", (20, 180, 40))

    assert api_service._resolve_image_input_for_vision("") is None
    assert api_service._resolve_image_input_for_vision("https://example.com/bird.jpg") == "https://example.com/bird.jpg"
    assert api_service._resolve_image_input_for_vision("data:image/png;base64,abc") == "data:image/png;base64,abc"

    encoded = api_service._resolve_image_input_for_vision(str(image_path))
    assert encoded.startswith("data:image/png;base64,")
    assert api_service._is_backend_accessible_image(str(image_path)) is True
    assert "dominant color=green-leaning" in api_service._build_visual_grounding_hint(str(image_path))
    assert "Visual evidence" in api_service._inject_visual_grounding("prompt", str(image_path))


def test_visual_hint_returns_unknown_for_missing_or_invalid_image():
    TEST_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    bad_image = TEST_IMAGE_DIR / "bad.jpg"
    bad_image.write_bytes(b"not an image")

    assert api_service._resolve_image_input_for_vision(str(TEST_IMAGE_DIR / "missing.jpg")) is None
    assert api_service._build_visual_grounding_hint(str(TEST_IMAGE_DIR / "missing.jpg")) == "unknown"
    assert api_service._build_visual_grounding_hint(str(bad_image)) == "unknown"


def test_deepseek_text_call_handles_config_success_and_bad_json():
    with patch.object(api_service.settings, "deepseek_api_key", ""):
        assert api_service._call_deepseek_chat("prompt") is None

    with patch.object(api_service.settings, "deepseek_api_key", "key"), patch.object(
        api_service.settings, "deepseek_base_url", ""
    ):
        assert api_service._call_deepseek_chat("prompt") is None

    payload = {"choices": [{"message": {"content": " generated text "}}]}
    with patch.object(api_service.settings, "deepseek_api_key", "key"), patch.object(
        api_service.settings, "deepseek_base_url", "https://deepseek.test"
    ), patch.object(api_service.urllib_request, "urlopen", return_value=_FakeHTTPResponse(payload)) as mock_urlopen:
        assert api_service._call_deepseek_chat("prompt", model="m", temperature=0.1, max_tokens=10) == "generated text"

    mock_urlopen.assert_called_once()

    with patch.object(api_service.settings, "deepseek_api_key", "key"), patch.object(
        api_service.settings, "deepseek_base_url", "https://deepseek.test"
    ), patch.object(api_service.urllib_request, "urlopen", return_value=_FakeHTTPResponse(b"{bad json")):
        assert api_service._call_deepseek_chat("prompt") is None


def test_deepseek_vision_call_handles_config_success_and_empty_result():
    image_path = _write_test_image("vision.jpg", (40, 80, 160))

    with patch.object(api_service.settings, "deepseek_api_key", ""):
        assert api_service._call_deepseek_vision_chat("prompt", str(image_path)) is None

    with patch.object(api_service.settings, "deepseek_api_key", "key"), patch.object(
        api_service, "_resolve_image_input_for_vision", return_value=None
    ):
        assert api_service._call_deepseek_vision_chat("prompt", str(image_path)) is None

    payload = {"choices": [{"message": {"content": " vision text "}}]}
    with patch.object(api_service.settings, "deepseek_api_key", "key"), patch.object(
        api_service.settings, "deepseek_base_url", "https://deepseek.test"
    ), patch.object(api_service.urllib_request, "urlopen", return_value=_FakeHTTPResponse(payload)):
        assert api_service._call_deepseek_vision_chat("prompt", str(image_path)) == "vision text"

    empty_payload = {"choices": [{"message": {"content": " "}}]}
    with patch.object(api_service.settings, "deepseek_api_key", "key"), patch.object(
        api_service.settings, "deepseek_base_url", "https://deepseek.test"
    ), patch.object(api_service.urllib_request, "urlopen", return_value=_FakeHTTPResponse(empty_payload)):
        assert api_service._call_deepseek_vision_chat("prompt", str(image_path)) is None


def test_vision_fact_extraction_parses_json_and_ignores_invalid():
    with patch.object(api_service, "_is_backend_accessible_image", return_value=False):
        assert api_service._extract_vision_facts("/uploads/a.jpg", None) is None

    raw = '{"species":"Mallard","mainColor":"green","location":"water_surface","action":"swimming","pose":"side","confidence":0.8}'
    with patch.object(api_service, "_is_backend_accessible_image", return_value=True), patch.object(
        api_service, "_call_deepseek_vision_chat", return_value=raw
    ):
        facts = api_service._extract_vision_facts("/uploads/a.jpg", {"birdName": "Mallard"})

    assert facts["species"] == "Mallard"
    assert facts["confidence"] == 0.8

    with patch.object(api_service, "_is_backend_accessible_image", return_value=True), patch.object(
        api_service, "_call_deepseek_vision_chat", return_value="no json"
    ):
        assert api_service._extract_vision_facts("/uploads/a.jpg", None) is None


def test_quality_retry_and_repeated_fragment_helpers():
    assert api_service._has_repeated_fragment("abcabcabc") is True
    assert api_service._has_repeated_fragment("one two three four") is False

    calls = iter(["bad", "this second response is good"])
    assert (
        api_service._call_with_quality_retry(lambda: next(calls), min_length=10, banned_templates=[])
        == "this second response is good"
    )

    calls = iter(["bad", "still bad"])
    assert api_service._call_with_quality_retry(lambda: next(calls), min_length=20, banned_templates=[]) is None


def test_generate_copy_helpers_format_fallbacks_and_normalization():
    bird_hint = {"birdName": "Mallard", "confidence": 0.8}
    facts = {"mainColor": "green", "location": "water_surface", "action": "swimming"}

    fallback_with_bird = api_service._fallback_generate_copy(bird_hint, vision_facts=facts)
    fallback_without_bird = api_service._fallback_generate_copy(None, vision_facts=facts)
    assert fallback_with_bird
    assert fallback_without_bird

    normalized = api_service._normalize_generate_copy(
        "#short",
        bird_hint,
        visual_hint="dominant color=green",
        vision_facts=facts,
    )
    assert normalized
    assert "#" not in normalized

    long_text = "a" * 120
    assert api_service._normalize_generate_copy(long_text, bird_hint)
    assert api_service._soften_generate_tone("") == ""
    assert api_service._soften_generate_tone("plain text")
    assert api_service._ensure_generate_mentions_bird("", bird_hint)
    assert api_service._ensure_generate_mentions_bird("plain text", None) == "plain text"


def test_polish_helpers_and_variants_cover_ai_and_fallback_paths():
    bird_hint = {"birdName": "Mallard"}

    assert api_service._fallback_polish_copy("", None)
    assert "Mallard" in api_service._fallback_polish_copy("original", bird_hint)
    assert api_service._normalize_polish_copy("```md\nbetter ABC\n```", "ABC original") == "better ABC"
    assert api_service._normalize_polish_copy("no anchors", "ABC original") == "ABC original"

    metas = [
        {"content": "lite ABC text", "elapsedMs": 2, "retryCount": 0, "fallback": False},
        {"content": "enhanced ABC text", "elapsedMs": 3, "retryCount": 1, "fallback": False},
    ]
    with patch.object(api_service, "_call_with_quality_retry_meta", side_effect=metas):
        variants, source, meta = api_service._generate_polish_variants("ABC original", "/uploads/a.jpg", bird_hint)

    assert source == "deepseek"
    assert variants["lite"] == "lite ABC text"
    assert variants["enhanced"] == "enhanced ABC text"
    assert meta["enhanced"]["retryCount"] == 1

    fallback_metas = [
        {"content": None, "elapsedMs": 1, "retryCount": 1, "fallback": True},
        {"content": None, "elapsedMs": 1, "retryCount": 1, "fallback": True},
    ]
    with patch.object(api_service, "_call_with_quality_retry_meta", side_effect=fallback_metas):
        variants, source, _ = api_service._generate_polish_variants("ABC original", "/uploads/a.jpg", bird_hint)

    assert source == "fallback"
    assert variants["lite"]


def test_polish_model_prefers_vision_then_falls_back_to_text():
    with patch.object(api_service, "_inject_visual_grounding", return_value="grounded"), patch.object(
        api_service, "_is_backend_accessible_image", return_value=True
    ), patch.object(api_service, "_call_deepseek_vision_chat", return_value="vision result") as mock_vision, patch.object(
        api_service, "_call_deepseek_chat"
    ) as mock_text:
        assert api_service._call_polish_model_with_optional_vision("prompt", "/uploads/a.jpg") == "vision result"

    mock_vision.assert_called_once()
    mock_text.assert_not_called()

    with patch.object(api_service, "_inject_visual_grounding", return_value="grounded"), patch.object(
        api_service, "_is_backend_accessible_image", return_value=False
    ), patch.object(api_service, "_call_deepseek_chat", return_value="text result"):
        assert api_service._call_polish_model_with_optional_vision("prompt", "/uploads/a.jpg") == "text result"


def test_generate_post_copywriting_covers_successful_generate_and_polish(fake_user):
    quality_success = {
        "content": "this generated copy is long enough to pass quality",
        "attempts": 1,
        "retryCount": 0,
        "fallback": False,
        "elapsedMs": 8,
    }

    with patch.object(api_service, "_is_backend_accessible_image", return_value=True), patch.object(
        api_service, "_resolve_bird_hint_for_copywriting", return_value={"birdName": "Mallard", "confidence": 0.9}
    ), patch.object(api_service, "_extract_vision_facts", return_value={"mainColor": "green"}), patch.object(
        api_service, "_build_visual_grounding_hint", return_value="dominant color=green"
    ), patch.object(api_service, "_call_with_quality_retry_meta", return_value=quality_success):
        data, err = api_service.generate_post_copywriting(fake_user, "generate", "/uploads/a.jpg", "")

    assert err is None
    assert data["source"] == "deepseek_vision"
    assert data["aiMeta"]["fallback"] is False

    variants = {
        "lite": "polished text",
        "enhanced": "enhanced text",
        "defaultVariant": "lite",
        "sources": {"lite": "deepseek", "enhanced": "deepseek"},
    }
    polish_meta = {
        "lite": {"elapsedMs": 2, "retryCount": 0, "fallback": False},
        "enhanced": {"elapsedMs": 3, "retryCount": 1, "fallback": False},
    }
    with patch.object(api_service, "_resolve_bird_hint_for_copywriting", return_value=None), patch.object(
        api_service, "_build_visual_grounding_hint", return_value="unknown"
    ), patch.object(api_service, "_call_with_quality_retry_meta", return_value={"content": None, "elapsedMs": 0, "retryCount": 0, "fallback": True}), patch.object(
        api_service, "_generate_polish_variants", return_value=(variants, "deepseek", polish_meta)
    ):
        data, err = api_service.generate_post_copywriting(fake_user, "polish", "/uploads/a.jpg", "original text")

    assert err is None
    assert data["mode"] == "polish"
    assert data["content"] == "polished text"
    assert data["aiMeta"]["variants"]["enhanced"]["retryCount"] == 1


def test_generate_post_copywriting_rejects_missing_or_inaccessible_image(fake_user):
    data, err = api_service.generate_post_copywriting(fake_user, "generate", "", "")
    assert data is None
    assert err[0] == 1001

    with patch.object(api_service, "_is_backend_accessible_image", return_value=False):
        data, err = api_service.generate_post_copywriting(fake_user, "generate", "/uploads/missing.jpg", "")

    assert data is None
    assert err[0] == 1001


def test_database_error_branches_return_service_error(fake_user):
    service_calls = [
        lambda: api_service.register_user("u", "u@example.com", "password"),
        lambda: api_service.login_user("u@example.com", "password"),
        lambda: api_service.recognize_bird_for_user(fake_user, "bird.jpg", b"image"),
        lambda: api_service.list_bird_records(fake_user, 1, 10),
        lambda: api_service.get_bird_record_detail(fake_user, 1),
        lambda: api_service.update_bird_record(fake_user, 1, "New"),
        lambda: api_service.delete_bird_record(fake_user, 1),
        lambda: api_service.create_post(fake_user, "content", None),
        lambda: api_service.list_posts(1, 10),
        lambda: api_service.get_post_detail(1),
        lambda: api_service.update_post(fake_user, 1, "content", None),
        lambda: api_service.delete_post(fake_user, 1),
        lambda: api_service.create_comment(fake_user, 1, "comment", None),
    ]

    with patch.object(api_service, "SessionLocal", _raising_session_factory()), patch.object(
        api_service, "_save_upload_file", return_value="/uploads/bird.jpg"
    ), patch.object(api_service, "_predict_bird_from_image", return_value=("Mallard", 0.8)):
        for call in service_calls:
            data, err = call()
            assert data is None
            assert err[0] == 1005


def test_like_post_handles_integrity_and_database_errors(fake_user):
    with patch.object(api_service, "SessionLocal", _raising_session_factory(IntegrityError("stmt", "params", "orig"))):
        data, err = api_service.like_post(fake_user, 1)
        assert data is None
        assert err[0] == 1009

    with patch.object(api_service, "SessionLocal", _raising_session_factory()):
        data, err = api_service.like_post(fake_user, 1)
        assert data is None
        assert err[0] == 1005


def test_bird_hint_and_recognition_helpers_cover_fallbacks(fake_user):
    db = MagicMock()
    db.scalar.return_value = SimpleNamespace(bird_name="Mallard", confidence=0.91)
    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        assert api_service._find_recent_bird_hint(fake_user["id"], "/uploads/a.jpg") == {
            "birdName": "Mallard",
            "confidence": 0.91,
        }

    with patch.object(api_service, "_find_recent_bird_hint", return_value={"birdName": "Mallard", "confidence": 0.9}):
        assert api_service._resolve_bird_hint_for_copywriting(fake_user["id"], "/uploads/a.jpg")["birdName"] == "Mallard"

    image_path = _write_test_image("recognition.jpg", (0, 180, 20))
    with patch.object(api_service, "_find_recent_bird_hint", return_value=None), patch.object(
        api_service, "_resolve_local_image_path", return_value=image_path
    ), patch.object(api_service, "_predict_bird_from_image", return_value=("Mallard", 0.78)):
        hint = api_service._resolve_bird_hint_for_copywriting(fake_user["id"], str(image_path))

    assert hint == {"birdName": "Mallard", "confidence": 0.78}

    with patch.object(api_service, "_load_bird_model", side_effect=RuntimeError("no torch")):
        assert api_service._predict_bird_from_image(image_path)[0] == "Mallard"

    assert api_service._map_project_bird_name("kingfisher") == "Common Kingfisher"
    assert api_service._map_project_bird_name("bee-eater") == "European Bee-eater"
    assert api_service._map_project_bird_name("unknown species") == "unknown species"


def test_upload_post_image_handles_missing_file_and_storage_failure(fake_user):
    assert api_service.upload_post_image(fake_user, None, b"x")[1][0] == 1006
    assert api_service.upload_post_image(fake_user, "bird.jpg", b"")[1][0] == 1006

    with patch.object(api_service, "_save_upload_file", side_effect=OSError("disk full")):
        data, err = api_service.upload_post_image(fake_user, "bird.jpg", b"x")

    assert data is None
    assert err == (1005, "Storage write failed", 500)


def test_post_and_comment_not_found_forbidden_branches(fake_user):
    db = MagicMock()

    with patch.object(api_service, "SessionLocal", _session_factory(db)):
        db.get.return_value = None
        assert api_service.update_post(fake_user, 1, "content", None)[1][0] == 1004
        assert api_service.delete_post(fake_user, 1)[1][0] == 1004
        assert api_service.like_post(fake_user, 1)[1][0] == 1004
        assert api_service.create_comment(fake_user, 1, "comment", None)[1][0] == 1004

        db.get.return_value = SimpleNamespace(id=1, user_id=999)
        assert api_service.delete_post(fake_user, 1)[1][0] == 1003

        post = SimpleNamespace(id=1, user_id=1, comment_count=0, updated_at=None)
        wrong_parent = SimpleNamespace(id=2, post_id=999)
        db.get.side_effect = [post, wrong_parent]
        assert api_service.create_comment(fake_user, 1, "comment", 2)[1][0] == 1004


def test_unauthorized_service_branches_return_1002():
    assert api_service.list_bird_records(None, 1, 10)[1][0] == 1002
    assert api_service.get_bird_record_detail(None, 1)[1][0] == 1002
    assert api_service.update_bird_record(None, 1, "New")[1][0] == 1002
    assert api_service.delete_bird_record(None, 1)[1][0] == 1002
    assert api_service.create_post(None, "content", None)[1][0] == 1002
    assert api_service.update_post(None, 1, "content", None)[1][0] == 1002
    assert api_service.delete_post(None, 1)[1][0] == 1002
    assert api_service.like_post(None, 1)[1][0] == 1002
    assert api_service.create_comment(None, 1, "comment", None)[1][0] == 1002
    assert api_service.generate_post_copywriting(None, "generate", "/uploads/a.jpg", "")[1][0] == 1002
