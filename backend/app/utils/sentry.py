from importlib import import_module

from app.core.config import settings


def configure_sentry():
    if not settings.sentry_dsn:
        return False

    sentry_sdk = import_module("sentry_sdk")
    fastapi_integration = import_module("sentry_sdk.integrations.fastapi")

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        integrations=[fastapi_integration.FastApiIntegration()],
        send_default_pii=False,
    )
    return True
