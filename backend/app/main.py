from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse, PlainTextResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.responses import error, success
from app.db.session import engine
from app.routes.auth import router as auth_router
from app.routes.birds import router as birds_router
from app.routes.posts import router as posts_router
from app.routes.users import router as users_router
from app.utils.logger import configure_logging, get_logger
from app.utils.metrics import metrics_collector
from app.utils.sentry import configure_sentry


app = FastAPI(title="AviAI API", version="0.3.0")
configure_logging()
configure_sentry()
logger = get_logger(__name__)
APP_VERSION = "0.3.0"

BACKEND_ROOT = Path(__file__).resolve().parents[1]
UPLOADS_DIR = BACKEND_ROOT / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


_STATUS_TO_ERROR = {
    400: (1001, "参数错误"),
    401: (1002, "未登录或 Token 无效"),
    403: (1003, "无权限"),
    404: (1004, "资源不存在"),
    409: (1009, "资源冲突"),
}


def get_database_status():
    try:
        if engine is None:
            return "disconnected"
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "connected"
    except (AttributeError, SQLAlchemyError):
        return "disconnected"


@app.middleware("http")
async def record_request_metrics(request, call_next):
    start_time = perf_counter()
    metrics_collector.start_request()
    status_code = 500
    recorded = False

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        duration_ms = (perf_counter() - start_time) * 1000
        metrics_collector.finish_request(status_code, duration_ms)
        recorded = True
        logger.exception(
            "request failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "client": request.client.host if request.client else None,
            },
        )
        raise
    finally:
        if not recorded:
            duration_ms = (perf_counter() - start_time) * 1000
            metrics_collector.finish_request(status_code, duration_ms)
            logger.info(
                "request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                    "client": request.client.host if request.client else None,
                },
            )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request, exc):
    return error(1001, "参数错误", 400, data={"detail": exc.errors()})


@app.exception_handler(Exception)
async def handle_unexpected_error(request, exc):
    if isinstance(exc, SQLAlchemyError):
        return error(1005, "服务内部错误", 500)
    status_code = getattr(exc, "status_code", None)
    if status_code in _STATUS_TO_ERROR:
        code, message = _STATUS_TO_ERROR[status_code]
        return error(code, message, status_code)
    return error(1005, "服务内部错误", 500)


@app.get("/api/v1/health")
def health_check():
    return success(
        {
            "service": "backend",
            "status": "running",
            "database": get_database_status(),
            "time": datetime.now(timezone.utc).isoformat(),
        }
    )


@app.get("/health", include_in_schema=False)
def docker_health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": APP_VERSION,
            "database": get_database_status(),
        }
    )


@app.get("/api/v1/metrics")
def metrics():
    return success(metrics_collector.snapshot())


@app.get("/metrics", include_in_schema=False)
def prometheus_metrics():
    return PlainTextResponse(
        metrics_collector.prometheus_text(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(birds_router)
app.include_router(posts_router)
