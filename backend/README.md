# Backend

## Quick Start

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at `http://localhost:8000`.

## API

- Health: `GET /api/v1/health`
- Current user (demo): `GET /api/v1/users/me`
- Bird recognize (demo): `POST /api/v1/birds/recognize` with `multipart/form-data` field `image`
