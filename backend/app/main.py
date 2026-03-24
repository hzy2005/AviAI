from datetime import datetime, timezone

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine


app = FastAPI(title="AviAI Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health_check():
    db_status = "disconnected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except SQLAlchemyError:
        db_status = "disconnected"

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "service": "backend",
            "status": "running",
            "database": db_status,
            "time": datetime.now(timezone.utc).isoformat(),
        },
    }


@app.get("/api/v1/users/me")
def get_current_user():
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "id": 1,
            "username": "birdlover",
            "email": "bird@example.com",
            "avatarUrl": "",
        },
    }


@app.post("/api/v1/birds/recognize")
async def recognize_bird(image: UploadFile = File(...)):
    # Demo response; real model inference can be integrated later.
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "recordId": 101,
            "fileName": image.filename,
            "birdName": "白鹭",
            "confidence": 0.93,
        },
    }
