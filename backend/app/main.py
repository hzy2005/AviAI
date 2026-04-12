from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.responses import success
from app.db.session import engine
from app.routes.auth import router as auth_router
from app.routes.birds import router as birds_router
from app.routes.posts import router as posts_router
from app.routes.users import router as users_router


app = FastAPI(title="AviAI API", version="0.3.0")

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

@app.get("/api/v1/health")
def health_check():
    db_status = "disconnected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except SQLAlchemyError:
        db_status = "disconnected"

    return success(
        {
            "service": "backend",
            "status": "running",
            "database": db_status,
            "time": datetime.now(timezone.utc).isoformat(),
        }
    )


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(birds_router)
app.include_router(posts_router)
