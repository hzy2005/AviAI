import importlib.util
import sys
import types
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _install_optional_ai_stubs():
    """Keep API tests importable on machines without local torch packages."""
    if importlib.util.find_spec("torch") is None and "torch" not in sys.modules:
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

    has_torchvision_models = (
        importlib.util.find_spec("torchvision") is not None
        and importlib.util.find_spec("torchvision.models") is not None
    )
    if not has_torchvision_models and "torchvision.models" not in sys.modules:
        torchvision_stub = types.ModuleType("torchvision")
        models_stub = types.ModuleType("torchvision.models")

        class _Weights:
            meta = {"categories": []}

            @staticmethod
            def transforms():
                return lambda image: image

        models_stub.ResNet18_Weights = types.SimpleNamespace(DEFAULT=_Weights())
        models_stub.resnet18 = lambda weights=None: types.SimpleNamespace(eval=lambda: None)
        torchvision_stub.models = models_stub
        sys.modules["torchvision"] = torchvision_stub
        sys.modules["torchvision.models"] = models_stub


_install_optional_ai_stubs()

try:
    import fastapi  # noqa: F401
except ImportError:
    pass


@pytest.fixture
def fake_user():
    return {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "avatarUrl": "",
        "createdAt": "2026-04-28T00:00:00+00:00",
    }


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    try:
        from app.main import app
    except Exception:
        yield
        return

    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()
