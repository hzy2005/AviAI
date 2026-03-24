# Backend

## Quick Start

```bash
cd backend
conda create -n aviai-backend python=3.11 -y
conda activate aviai-backend
python -m pip install -r requirements.txt
# copy .env.example to .env and adjust DB account/password
alembic upgrade head
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at `http://localhost:8000`.

## API

- Health: `GET /api/v1/health`
- Current user (demo): `GET /api/v1/users/me`
- Bird recognize (demo): `POST /api/v1/birds/recognize` with `multipart/form-data` field `image`

## Database Migration

```bash
cd backend
conda activate aviai-backend
alembic upgrade head
```

Create new migration:

```bash
alembic revision -m "your change name"
```
