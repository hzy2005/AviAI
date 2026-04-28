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
