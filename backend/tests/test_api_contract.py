from unittest.mock import MagicMock, patch

from app.main import app
from app.routes.deps import get_current_user


def assert_response_envelope(body, code):
    assert body["code"] == code
    assert "message" in body
    assert "msg" in body
    assert "data" in body


def authenticate_as(fake_user):
    app.dependency_overrides[get_current_user] = lambda: fake_user


def test_health_returns_running_status(client):
    db_context = MagicMock()
    db_context.__enter__.return_value = MagicMock()
    db_context.__exit__.return_value = False
    fake_engine = MagicMock()
    fake_engine.connect.return_value = db_context

    with patch("app.main.engine", fake_engine):
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert_response_envelope(body, 0)
    assert body["data"]["service"] == "backend"
    assert body["data"]["status"] == "running"
    assert body["data"]["database"] == "connected"
    fake_engine.connect.assert_called_once()


def test_login_success_returns_token(client):
    login_data = {
        "token": "test-token",
        "user": {"id": 1, "username": "tester", "avatarUrl": ""},
    }

    with patch("app.routes.auth.api_service.login_user", return_value=(login_data, None)) as mock_login:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "tester@example.com", "password": "12345678"},
        )

    assert response.status_code == 200
    body = response.json()
    assert_response_envelope(body, 0)
    assert body["data"]["token"] == "test-token"
    mock_login.assert_called_once_with("tester@example.com", "12345678")


def test_login_missing_email_returns_validation_error(client):
    response = client.post("/api/v1/auth/login", json={"password": "12345678"})

    assert response.status_code == 400
    body = response.json()
    assert_response_envelope(body, 1001)
    assert body["data"]["detail"]


def test_users_me_without_login_returns_unauthorized(client):
    with patch(
        "app.routes.users.api_service.get_user_profile",
        return_value=(None, (1002, "Unauthorized", 401)),
    ) as mock_profile:
        response = client.get("/api/v1/users/me")

    assert response.status_code == 401
    body = response.json()
    assert_response_envelope(body, 1002)
    assert body["data"] is None
    mock_profile.assert_called_once_with(None)


def test_create_post_without_login_returns_unauthorized(client):
    with patch(
        "app.routes.posts.api_service.create_post",
        return_value=(None, (1002, "Unauthorized", 401)),
    ) as mock_create:
        response = client.post(
            "/api/v1/posts",
            json={"content": "hello bird", "imageUrl": None},
        )

    assert response.status_code == 401
    body = response.json()
    assert_response_envelope(body, 1002)
    assert body["data"] is None
    mock_create.assert_called_once_with(None, "hello bird", None)


def test_list_posts_returns_pagination_shape(client):
    posts_data = {
        "list": [
            {
                "postId": 1,
                "content": "first post",
                "imageUrl": None,
                "likeCount": 0,
                "commentCount": 0,
                "createdAt": "2026-04-28T00:00:00+00:00",
                "updatedAt": "2026-04-28T00:00:00+00:00",
                "author": {"id": 1, "username": "tester", "avatarUrl": ""},
            }
        ],
        "total": 1,
        "page": 1,
        "pageSize": 10,
    }

    with patch("app.routes.posts.api_service.list_posts", return_value=(posts_data, None)) as mock_list:
        response = client.get("/api/v1/posts?page=1&pageSize=10&keyword=bird")

    assert response.status_code == 200
    body = response.json()
    assert_response_envelope(body, 0)
    assert set(body["data"].keys()) == {"list", "total", "page", "pageSize"}
    assert body["data"]["list"][0]["postId"] == 1
    mock_list.assert_called_once_with(1, 10, "bird")


def test_ai_copywriting_parameter_error_returns_1001(client, fake_user):
    authenticate_as(fake_user)
    service_error = (1001, "content is required when mode is polish.", 400)

    with patch(
        "app.routes.posts.api_service.generate_post_copywriting",
        return_value=(None, service_error),
    ) as mock_ai:
        response = client.post(
            "/api/v1/posts/ai-copywriting",
            json={"mode": "polish", "imageUrl": "/uploads/bird.jpg", "content": ""},
        )

    assert response.status_code == 400
    body = response.json()
    assert_response_envelope(body, 1001)
    assert body["data"] is None
    mock_ai.assert_called_once_with(
        current_user=fake_user,
        mode="polish",
        image_url="/uploads/bird.jpg",
        content="",
    )


def test_recognize_without_login_returns_unauthorized(client):
    with patch(
        "app.routes.birds.api_service.recognize_bird_for_user",
        return_value=(None, (1002, "Unauthorized", 401)),
    ) as mock_recognize:
        response = client.post(
            "/api/v1/birds/recognize",
            files={"image": ("bird.jpg", b"fake-image", "image/jpeg")},
        )

    assert response.status_code == 401
    body = response.json()
    assert_response_envelope(body, 1002)
    assert body["data"] is None
    mock_recognize.assert_called_once_with(None, "bird.jpg", b"fake-image")


def test_post_detail_not_found_returns_1004(client):
    with patch(
        "app.routes.posts.api_service.get_post_detail",
        return_value=(None, (1004, "Resource not found.", 404)),
    ) as mock_detail:
        response = client.get("/api/v1/posts/999")

    assert response.status_code == 404
    body = response.json()
    assert_response_envelope(body, 1004)
    assert body["data"] is None
    mock_detail.assert_called_once_with(999)


def test_create_comment_missing_content_returns_validation_error(client, fake_user):
    authenticate_as(fake_user)

    response = client.post("/api/v1/posts/1/comments", json={"parentId": None})

    assert response.status_code == 400
    body = response.json()
    assert_response_envelope(body, 1001)
    assert body["data"]["detail"]
