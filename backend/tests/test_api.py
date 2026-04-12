import io
import sys
import unittest
import uuid
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
        self.case_id = uuid.uuid4().hex[:8]

    def login(self):
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "bird@example.com", "password": "12345678"},
        )
        if response.status_code != 200:
            self.client.post(
                "/api/v1/auth/register",
                json={
                    "username": f"birdlover_{self.case_id}",
                    "email": "bird@example.com",
                    "password": "12345678",
                },
            )
            response = self.client.post(
                "/api/v1/auth/login",
                json={"email": "bird@example.com", "password": "12345678"},
            )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["token"]

    def register_and_login(self, username, email, password="12345678"):
        register_response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )
        self.assertIn(register_response.status_code, {201, 409})
        login_response = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        self.assertEqual(login_response.status_code, 200)
        return login_response.json()["data"]["token"]

    def assert_post_contract_shape(self, post_data):
        self.assertSetEqual(
            set(post_data.keys()),
            {
                "postId",
                "content",
                "imageUrl",
                "likeCount",
                "commentCount",
                "createdAt",
                "updatedAt",
                "author",
            },
        )
        self.assertIsInstance(post_data["postId"], int)
        self.assertIsInstance(post_data["content"], str)
        self.assertIn(type(post_data["imageUrl"]), {str, type(None)})
        self.assertIsInstance(post_data["likeCount"], int)
        self.assertIsInstance(post_data["commentCount"], int)
        self.assertIsInstance(post_data["createdAt"], str)
        self.assertIsInstance(post_data["updatedAt"], str)
        self.assertSetEqual(
            set(post_data["author"].keys()),
            {"id", "username", "avatarUrl"},
        )

    def test_posts_contract_list_and_detail_shape(self):
        token = self.login()
        headers = {"Authorization": f"Bearer {token}"}

        create_post_response = self.client.post(
            "/api/v1/posts",
            headers=headers,
            json={
                "content": "contract post content",
                "imageUrl": "/uploads/contract-post.jpg",
            },
        )
        self.assertEqual(create_post_response.status_code, 201)
        created_post_id = create_post_response.json()["data"]["postId"]

        list_response = self.client.get("/api/v1/posts?page=1&pageSize=10&keyword=contract")
        self.assertEqual(list_response.status_code, 200)
        list_body = list_response.json()
        self.assertEqual(list_body["code"], 0)
        self.assertEqual(list_body["message"], "ok")
        self.assertSetEqual(
            set(list_body["data"].keys()),
            {"list", "total", "page", "pageSize"},
        )
        self.assertEqual(list_body["data"]["page"], 1)
        self.assertEqual(list_body["data"]["pageSize"], 10)
        self.assertGreaterEqual(list_body["data"]["total"], 1)

        matched_item = next(
            (
                item
                for item in list_body["data"]["list"]
                if item["postId"] == created_post_id
            ),
            None,
        )
        self.assertIsNotNone(matched_item)
        self.assert_post_contract_shape(matched_item)

        detail_response = self.client.get(f"/api/v1/posts/{created_post_id}")
        self.assertEqual(detail_response.status_code, 200)
        detail_body = detail_response.json()
        self.assertEqual(detail_body["code"], 0)
        self.assertEqual(detail_body["message"], "ok")
        self.assert_post_contract_shape(detail_body["data"])
        self.assertEqual(detail_body["data"]["postId"], created_post_id)

    def test_posts_write_contract_error_codes(self):
        owner_token = self.login()
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        other_token = self.register_and_login(
            username=f"post-other-user-{self.case_id}",
            email=f"post-other-{self.case_id}@example.com",
        )
        other_headers = {"Authorization": f"Bearer {other_token}"}

        create_unauthorized = self.client.post(
            "/api/v1/posts",
            json={"content": "unauthorized create", "imageUrl": None},
        )
        self.assertEqual(create_unauthorized.status_code, 401)
        self.assertEqual(create_unauthorized.json()["code"], 1002)

        created = self.client.post(
            "/api/v1/posts",
            headers=owner_headers,
            json={"content": "post write contract", "imageUrl": "/uploads/pc.jpg"},
        )
        self.assertEqual(created.status_code, 201)
        created_post_id = created.json()["data"]["postId"]

        update_unauthorized = self.client.put(
            f"/api/v1/posts/{created_post_id}",
            json={"content": "update without auth", "imageUrl": None},
        )
        self.assertEqual(update_unauthorized.status_code, 401)
        self.assertEqual(update_unauthorized.json()["code"], 1002)

        update_not_found = self.client.put(
            "/api/v1/posts/999999",
            headers=owner_headers,
            json={"content": "missing post", "imageUrl": None},
        )
        self.assertEqual(update_not_found.status_code, 404)
        self.assertEqual(update_not_found.json()["code"], 1004)

        update_forbidden = self.client.put(
            f"/api/v1/posts/{created_post_id}",
            headers=other_headers,
            json={"content": "forbidden update", "imageUrl": None},
        )
        self.assertEqual(update_forbidden.status_code, 403)
        self.assertEqual(update_forbidden.json()["code"], 1003)

        delete_unauthorized = self.client.delete(f"/api/v1/posts/{created_post_id}")
        self.assertEqual(delete_unauthorized.status_code, 401)
        self.assertEqual(delete_unauthorized.json()["code"], 1002)

        delete_not_found = self.client.delete("/api/v1/posts/999998", headers=owner_headers)
        self.assertEqual(delete_not_found.status_code, 404)
        self.assertEqual(delete_not_found.json()["code"], 1004)

        delete_forbidden = self.client.delete(
            f"/api/v1/posts/{created_post_id}",
            headers=other_headers,
        )
        self.assertEqual(delete_forbidden.status_code, 403)
        self.assertEqual(delete_forbidden.json()["code"], 1003)

        like_unauthorized = self.client.post(f"/api/v1/posts/{created_post_id}/like")
        self.assertEqual(like_unauthorized.status_code, 401)
        self.assertEqual(like_unauthorized.json()["code"], 1002)

        like_not_found = self.client.post("/api/v1/posts/999997/like", headers=owner_headers)
        self.assertEqual(like_not_found.status_code, 404)
        self.assertEqual(like_not_found.json()["code"], 1004)

        like_success = self.client.post(
            f"/api/v1/posts/{created_post_id}/like",
            headers=owner_headers,
        )
        self.assertEqual(like_success.status_code, 200)
        self.assertEqual(like_success.json()["code"], 0)

        like_conflict = self.client.post(
            f"/api/v1/posts/{created_post_id}/like",
            headers=owner_headers,
        )
        self.assertEqual(like_conflict.status_code, 409)
        self.assertEqual(like_conflict.json()["code"], 1009)

        comment_unauthorized = self.client.post(
            f"/api/v1/posts/{created_post_id}/comments",
            json={"content": "unauthorized comment", "parentId": None},
        )
        self.assertEqual(comment_unauthorized.status_code, 401)
        self.assertEqual(comment_unauthorized.json()["code"], 1002)

        comment_not_found = self.client.post(
            "/api/v1/posts/999996/comments",
            headers=owner_headers,
            json={"content": "missing post comment", "parentId": None},
        )
        self.assertEqual(comment_not_found.status_code, 404)
        self.assertEqual(comment_not_found.json()["code"], 1004)

    def test_posts_persistence_after_like_and_comment(self):
        token = self.login()
        headers = {"Authorization": f"Bearer {token}"}

        create_response = self.client.post(
            "/api/v1/posts",
            headers=headers,
            json={"content": "persistence post", "imageUrl": "/uploads/persistence.jpg"},
        )
        self.assertEqual(create_response.status_code, 201)
        post_id = create_response.json()["data"]["postId"]

        like_response = self.client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
        self.assertEqual(like_response.status_code, 200)

        comment_response = self.client.post(
            f"/api/v1/posts/{post_id}/comments",
            headers=headers,
            json={"content": "persisted comment", "parentId": None},
        )
        self.assertEqual(comment_response.status_code, 201)

        detail_response = self.client.get(f"/api/v1/posts/{post_id}")
        self.assertEqual(detail_response.status_code, 200)
        detail_data = detail_response.json()["data"]
        self.assertEqual(detail_data["likeCount"], 1)
        self.assertEqual(detail_data["commentCount"], 1)

        list_response = self.client.get("/api/v1/posts?page=1&pageSize=10&keyword=persistence")
        self.assertEqual(list_response.status_code, 200)
        list_item = next(
            (item for item in list_response.json()["data"]["list"] if item["postId"] == post_id),
            None,
        )
        self.assertIsNotNone(list_item)
        self.assertEqual(list_item["likeCount"], 1)
        self.assertEqual(list_item["commentCount"], 1)

    def test_health(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 0)

    def test_register_and_login(self):
        register_response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": f"newbirder-{self.case_id}",
                "email": f"newbirder-{self.case_id}@example.com",
                "password": "12345678",
            },
        )
        self.assertEqual(register_response.status_code, 201)

        login_response = self.client.post(
            "/api/v1/auth/login",
            json={"email": f"newbirder-{self.case_id}@example.com", "password": "12345678"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("token", login_response.json()["data"])

        logout_response = self.client.post("/api/v1/auth/logout")
        self.assertEqual(logout_response.status_code, 200)
        self.assertTrue(logout_response.json()["data"]["success"])

    def test_auth_contract_shape(self):
        register_response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": f"contract-user-{self.case_id}",
                "email": f"contract-{self.case_id}@example.com",
                "password": "12345678",
            },
        )
        self.assertEqual(register_response.status_code, 201)
        register_body = register_response.json()
        self.assertEqual(register_body["code"], 0)
        self.assertEqual(register_body["message"], "ok")
        self.assertIn("userId", register_body["data"])

        login_response = self.client.post(
            "/api/v1/auth/login",
            json={"email": f"contract-{self.case_id}@example.com", "password": "12345678"},
        )
        self.assertEqual(login_response.status_code, 200)
        login_body = login_response.json()
        self.assertEqual(login_body["code"], 0)
        self.assertEqual(login_body["message"], "ok")
        self.assertIn("token", login_body["data"])
        self.assertIn("user", login_body["data"])
        self.assertSetEqual(
            set(login_body["data"]["user"].keys()),
            {"id", "username", "avatarUrl"},
        )

        token = login_body["data"]["token"]
        me_response = self.client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me_response.status_code, 200)
        me_body = me_response.json()
        self.assertEqual(me_body["code"], 0)
        self.assertEqual(me_body["message"], "ok")
        self.assertSetEqual(
            set(me_body["data"].keys()),
            {"id", "username", "email", "avatarUrl", "createdAt"},
        )
        self.assertEqual(me_body["data"]["email"], f"contract-{self.case_id}@example.com")

        logout_response = self.client.post("/api/v1/auth/logout")
        self.assertEqual(logout_response.status_code, 200)
        logout_body = logout_response.json()
        self.assertEqual(logout_body["code"], 0)
        self.assertEqual(logout_body["message"], "ok")
        self.assertSetEqual(set(logout_body["data"].keys()), {"success"})
        self.assertTrue(logout_body["data"]["success"])

    def test_auth_contract_users_me_unauthorized(self):
        response = self.client.get("/api/v1/users/me")
        self.assertEqual(response.status_code, 401)
        body = response.json()
        self.assertEqual(body["code"], 1002)
        self.assertIsNone(body["data"])

    def test_birds_contract_shape_and_records_visibility(self):
        token = self.login()
        headers = {"Authorization": f"Bearer {token}"}

        recognize_response = self.client.post(
            "/api/v1/birds/recognize",
            headers=headers,
            files={"image": ("contract-bird.png", io.BytesIO(b"fake-image"), "image/png")},
        )
        self.assertEqual(recognize_response.status_code, 201)
        recognize_body = recognize_response.json()
        self.assertEqual(recognize_body["code"], 0)
        self.assertEqual(recognize_body["message"], "ok")
        self.assertSetEqual(
            set(recognize_body["data"].keys()),
            {"recordId", "birdName", "confidence", "imageUrl", "createdAt"},
        )
        self.assertGreaterEqual(recognize_body["data"]["confidence"], 0)
        self.assertLessEqual(recognize_body["data"]["confidence"], 1)
        created_record_id = recognize_body["data"]["recordId"]

        records_response = self.client.get(
            "/api/v1/birds/records?page=1&pageSize=10",
            headers=headers,
        )
        self.assertEqual(records_response.status_code, 200)
        records_body = records_response.json()
        self.assertEqual(records_body["code"], 0)
        self.assertEqual(records_body["message"], "ok")
        self.assertSetEqual(
            set(records_body["data"].keys()),
            {"list", "total", "page", "pageSize"},
        )
        self.assertEqual(records_body["data"]["page"], 1)
        self.assertEqual(records_body["data"]["pageSize"], 10)
        self.assertGreaterEqual(records_body["data"]["total"], 1)
        self.assertTrue(
            any(item["recordId"] == created_record_id for item in records_body["data"]["list"])
        )

    def test_birds_contract_unauthorized_and_invalid_file(self):
        records_unauthorized = self.client.get("/api/v1/birds/records")
        self.assertEqual(records_unauthorized.status_code, 401)
        records_unauthorized_body = records_unauthorized.json()
        self.assertEqual(records_unauthorized_body["code"], 1002)
        self.assertIsNone(records_unauthorized_body["data"])

        recognize_unauthorized = self.client.post(
            "/api/v1/birds/recognize",
            files={"image": ("no-token.jpg", io.BytesIO(b"fake-image"), "image/jpeg")},
        )
        self.assertEqual(recognize_unauthorized.status_code, 401)
        recognize_unauthorized_body = recognize_unauthorized.json()
        self.assertEqual(recognize_unauthorized_body["code"], 1002)
        self.assertIsNone(recognize_unauthorized_body["data"])

        token = self.login()
        headers = {"Authorization": f"Bearer {token}"}
        recognize_invalid_file = self.client.post(
            "/api/v1/birds/recognize",
            headers=headers,
            files={"image": ("not-image.txt", io.BytesIO(b"fake-text"), "text/plain")},
        )
        self.assertEqual(recognize_invalid_file.status_code, 400)
        recognize_invalid_file_body = recognize_invalid_file.json()
        self.assertEqual(recognize_invalid_file_body["code"], 1006)
        self.assertIsNone(recognize_invalid_file_body["data"])

    def test_user_and_records(self):
        token = self.login()
        headers = {"Authorization": f"Bearer {token}"}

        user_response = self.client.get("/api/v1/users/me", headers=headers)
        self.assertEqual(user_response.status_code, 200)
        self.assertEqual(user_response.json()["data"]["email"], "bird@example.com")

        recognize_response = self.client.post(
            "/api/v1/birds/recognize",
            headers=headers,
            files={"image": ("records-check.jpg", io.BytesIO(b"fake-image"), "image/jpeg")},
        )
        self.assertEqual(recognize_response.status_code, 201)

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
