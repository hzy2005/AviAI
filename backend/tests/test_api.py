import io
import sys
import unittest
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
BACKEND_ROOT = CURRENT_FILE.parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient

from app.main import app
from app.mock_data import reset_store


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        reset_store()
        self.client = TestClient(app)

    def login(self):
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "bird@example.com", "password": "12345678"},
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["token"]

    def test_health(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 0)

    def test_register_and_login(self):
        register_response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": "newbirder",
                "email": "newbirder@example.com",
                "password": "12345678",
            },
        )
        self.assertEqual(register_response.status_code, 201)

        login_response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "newbirder@example.com", "password": "12345678"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("token", login_response.json()["data"])

        logout_response = self.client.post("/api/v1/auth/logout")
        self.assertEqual(logout_response.status_code, 200)
        self.assertTrue(logout_response.json()["data"]["success"])

    def test_user_and_records(self):
        token = self.login()
        headers = {"Authorization": f"Bearer {token}"}

        user_response = self.client.get("/api/v1/users/me", headers=headers)
        self.assertEqual(user_response.status_code, 200)
        self.assertEqual(user_response.json()["data"]["email"], "bird@example.com")

        records_response = self.client.get("/api/v1/birds/records", headers=headers)
        self.assertEqual(records_response.status_code, 200)
        self.assertGreaterEqual(records_response.json()["data"]["total"], 1)

    def test_recognize_post_crud_like_comment_flow(self):
        token = self.login()
        headers = {"Authorization": f"Bearer {token}"}

        recognize_response = self.client.post(
            "/api/v1/birds/recognize",
            headers=headers,
            files={"image": ("egret.jpg", io.BytesIO(b"fake-image"), "image/jpeg")},
        )
        self.assertEqual(recognize_response.status_code, 201)

        create_post_response = self.client.post(
            "/api/v1/posts",
            headers=headers,
            json={"content": "测试动态", "imageUrl": "/uploads/test.jpg"},
        )
        self.assertEqual(create_post_response.status_code, 201)
        post_id = create_post_response.json()["data"]["postId"]

        list_response = self.client.get("/api/v1/posts?keyword=测试")
        self.assertEqual(list_response.status_code, 200)
        self.assertGreaterEqual(list_response.json()["data"]["total"], 1)

        detail_response = self.client.get(f"/api/v1/posts/{post_id}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["data"]["postId"], post_id)

        update_response = self.client.put(
            f"/api/v1/posts/{post_id}",
            headers=headers,
            json={"content": "更新后的动态", "imageUrl": "/uploads/updated.jpg"},
        )
        self.assertEqual(update_response.status_code, 200)

        like_response = self.client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
        self.assertEqual(like_response.status_code, 200)
        self.assertTrue(like_response.json()["data"]["liked"])

        comment_response = self.client.post(
            f"/api/v1/posts/{post_id}/comments",
            headers=headers,
            json={"content": "测试评论", "parentId": None},
        )
        self.assertEqual(comment_response.status_code, 201)

        delete_response = self.client.delete(f"/api/v1/posts/{post_id}", headers=headers)
        self.assertEqual(delete_response.status_code, 200)
        self.assertTrue(delete_response.json()["data"]["deleted"])


if __name__ == "__main__":
    unittest.main()
