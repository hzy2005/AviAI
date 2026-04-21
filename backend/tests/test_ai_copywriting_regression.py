import sys
import unittest
from pathlib import Path
import types
from unittest.mock import patch

CURRENT_FILE = Path(__file__).resolve()
BACKEND_ROOT = CURRENT_FILE.parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

if "fastapi" not in sys.modules:
    fastapi_stub = types.ModuleType("fastapi")
    fastapi_stub.Header = lambda default=None: default
    sys.modules["fastapi"] = fastapi_stub

if "app.db.session" not in sys.modules:
    db_session_stub = types.ModuleType("app.db.session")

    class _DummySession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    db_session_stub.SessionLocal = lambda: _DummySession()
    db_session_stub.engine = None
    sys.modules["app.db.session"] = db_session_stub

# Lightweight stubs so tests can import api_service without local torch install.
if "torch" not in sys.modules:
    torch_stub = types.ModuleType("torch")

    class _NoGrad:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    torch_stub.no_grad = lambda: _NoGrad()
    nn_stub = types.ModuleType("torch.nn")
    functional_stub = types.ModuleType("torch.nn.functional")
    functional_stub.softmax = lambda logits, dim=1: logits
    nn_stub.functional = functional_stub
    torch_stub.nn = nn_stub
    sys.modules["torch"] = torch_stub
    sys.modules["torch.nn"] = nn_stub
    sys.modules["torch.nn.functional"] = functional_stub

if "torchvision.models" not in sys.modules:
    tv_stub = types.ModuleType("torchvision")
    models_stub = types.ModuleType("torchvision.models")

    class _Weights:
        meta = {"categories": []}

        @staticmethod
        def transforms():
            return lambda img: img

    models_stub.ResNet18_Weights = types.SimpleNamespace(DEFAULT=_Weights())
    models_stub.resnet18 = lambda weights=None: types.SimpleNamespace(eval=lambda: None)
    tv_stub.models = models_stub
    sys.modules["torchvision"] = tv_stub
    sys.modules["torchvision.models"] = models_stub

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
        ), patch.object(
            api_service,
            "_find_recent_bird_hint",
            return_value={"birdName": "Mallard", "confidence": 0.9},
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
