import unittest
from unittest.mock import patch

from app.services import api_service


class AICopywritingRegressionTest(unittest.TestCase):
    def test_generate_contract_shape(self):
        user = {"id": 1}
        with patch.object(
            api_service,
            "_call_with_quality_retry_meta",
            return_value={
                "content": "清晨湖边雾气很轻，枝头鸟影停得很稳。羽色在逆光里层次分明，抬头姿态很警觉。站着看了好一会儿，心里也慢慢安静下来。",
                "attempts": 1,
                "retryCount": 0,
                "fallback": False,
                "elapsedMs": 123,
            },
        ), patch.object(api_service, "_find_recent_bird_hint", return_value={"birdName": "Mallard", "confidence": 0.92}):
            data, err = api_service.generate_post_copywriting(
                current_user=user,
                mode="generate",
                image_url="/uploads/a.jpg",
                content="",
            )

        self.assertIsNone(err)
        self.assertEqual(data["mode"], "generate")
        self.assertIsInstance(data["content"], str)
        self.assertTrue(data["content"])
        self.assertIn(data["source"], {"deepseek_vision", "deepseek", "fallback"})
        self.assertIn("aiMeta", data)
        self.assertEqual(data["aiMeta"]["mode"], "generate")
        self.assertIn("model", data["aiMeta"])
        self.assertIn("elapsedMs", data["aiMeta"])
        self.assertIn("retryCount", data["aiMeta"])
        self.assertIn("fallback", data["aiMeta"])

    def test_polish_contract_shape_with_variants(self):
        user = {"id": 1}
        with patch.object(
            api_service,
            "_generate_polish_variants",
            return_value=(
                {
                    "lite": "今天在公园看到一只小鸟，停在枝头很安静，越看越有意思。",
                    "enhanced": "午后公园里，一只小鸟安静停在枝头，细小动作很有节奏感，让人忍不住多看几眼。",
                    "defaultVariant": "lite",
                    "sources": {"lite": "deepseek", "enhanced": "deepseek"},
                },
                "deepseek",
                {
                    "lite": {"model": "deepseek-chat", "elapsedMs": 101, "retryCount": 0, "fallback": False},
                    "enhanced": {"model": "deepseek-chat", "elapsedMs": 131, "retryCount": 1, "fallback": False},
                },
            ),
        ), patch.object(
            api_service,
            "_call_with_quality_retry_meta",
            return_value={"content": "stub", "attempts": 1, "retryCount": 0, "fallback": False, "elapsedMs": 1},
        ):
            data, err = api_service.generate_post_copywriting(
                current_user=user,
                mode="polish",
                image_url="/uploads/a.jpg",
                content="今天在公园看到一只小鸟",
            )

        self.assertIsNone(err)
        self.assertEqual(data["mode"], "polish")
        self.assertEqual(data["defaultVariant"], "lite")
        self.assertEqual(data["content"], data["lite"])
        self.assertIn("enhanced", data)
        self.assertIn("sources", data)
        self.assertIn("aiMeta", data)
        self.assertEqual(data["aiMeta"]["mode"], "polish")
        self.assertIn("variants", data["aiMeta"])

    def test_generate_fallback_when_quality_fails(self):
        user = {"id": 1}
        with patch.object(
            api_service,
            "_call_with_quality_retry_meta",
            return_value={"content": None, "attempts": 2, "retryCount": 1, "fallback": True, "elapsedMs": 88},
        ), patch.object(api_service, "_find_recent_bird_hint", return_value={"birdName": "Mallard", "confidence": 0.8}):
            data, err = api_service.generate_post_copywriting(
                current_user=user,
                mode="generate",
                image_url="/uploads/fallback.jpg",
                content="",
            )

        self.assertIsNone(err)
        self.assertEqual(data["source"], "fallback")
        self.assertTrue(data["aiMeta"]["fallback"])
        self.assertGreaterEqual(data["aiMeta"]["retryCount"], 1)
        self.assertTrue(data["content"])


if __name__ == "__main__":
    unittest.main()
