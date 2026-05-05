# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AviAI** is a bird recognition and community platform consisting of a WeChat Mini Program frontend and a FastAPI backend. Users can photograph birds for AI-powered identification, browse a bird encyclopedia, and interact in a community.

## Commands

### Backend

```bash
# Setup (one-time)
cd backend
conda create -n aviai-backend python=3.11
conda activate aviai-backend
pip install -r requirements.txt
cp .env.example .env  # then fill in values

# Run database migrations
alembic upgrade head

# Start dev server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Lint
ruff check backend/

# Test (all)
coverage run -m pytest backend/tests -c backend/pytest.ini

# Test (single test)
pytest tests/test_api.py::ApiTestCase::test_health_check -v
```

### Frontend

```bash
# Setup
cd frontend && npm ci

# Lint
npm run lint
npm run lint:fix

# Format
npm run format

# Test (all)
npm test

# Test (single file)
node --test src/__tests__/page-interactions.test.js

# Run: open frontend/ directory in WeChat DevTools
```

## Architecture

### System Overview

Three-tier architecture: WeChat Mini Program → FastAPI backend → MySQL + Redis.

- All API endpoints are prefixed with `/api/v1`
- Unified response envelope: `{code: 0, message: "ok", data: {...}}` for success; error codes 1001–1009 for failures
- Authentication via JWT Bearer token in the `Authorization` header
- Images are uploaded as multipart form-data and stored in `backend/uploads/`

### Backend (`backend/`)

- `app/main.py` — FastAPI app initialization (v0.3.0), CORS middleware, route registration, error handlers
- `app/routes/` — Thin route handlers: `auth.py`, `birds.py`, `posts.py`, `users.py`, `deps.py` (shared dependencies/auth guards)
- `app/services/api_service.py` — Central business logic (~51KB): recognition, AI copywriting, community interactions
- `app/schemas.py` — All Pydantic request/response schemas (RegisterRequest, LoginRequest, CreatePostRequest, etc.)
- `app/models/` — SQLAlchemy ORM models: `user.py`, `post.py`, `bird_record.py`, `comment.py`, `like.py`
- `app/core/auth.py` — JWT creation/validation
- `app/core/config.py` — Pydantic Settings loaded from `.env`
- `app/core/responses.py` — Standardized response helpers
- `app/db/` — SQLAlchemy session setup (`session.py`, `base.py`, `base_model.py`)
- `backend/migrations/` — Alembic migration scripts

Bird recognition uses PyTorch (ResNet18) for local classification and the DeepSeek vision API for detailed identification (configured via `DEEPSEEK_VISION_MODEL`). AI copywriting also uses DeepSeek. Set `USE_MOCK_DATA=true` in `.env` to bypass real AI/DB calls during development.

CI uses Python 3.12 with SQLite in-memory (`DATABASE_URL=sqlite:///:memory:`); local development requires MySQL.

### Frontend (`frontend/`)

- `utils/request.js` — All HTTP calls go through this centralized wrapper (handles auth header injection and offline mock routing)
- `utils/mock-api.js` — Mock responses for offline development (enabled by default via `config/env.js`)
- `utils/api.js` — API call definitions
- `utils/auth.js` — Token storage/retrieval helpers
- `config/env.js` — Switch between dev (localhost for simulator), LAN (192.168.x.x for real device), and production base URLs; mock API toggle
- `pages/` — 12 pages: index, login, register, recognize, bird-detail, community, community-detail, encyclopedia, history, profile, profile-edit, splash

### Key Data Flows

1. **Bird Recognition**: Frontend uploads image → `POST /api/v1/birds/recognize` (multipart) → `api_service.py` runs ResNet18 classification + DeepSeek vision → result stored in `bird_record` → returned to frontend
2. **Community Posts**: `POST /api/v1/posts` → service creates post + images in DB → `GET /api/v1/posts` uses Redis-cached timeline
3. **Auth**: `POST /api/v1/auth/login` → JWT issued → stored in frontend storage → sent as `Authorization: Bearer <token>` on subsequent requests

## Conventions

- Never bypass parameter validation or auth checks
- Keep `docs/` in sync when changing API contracts or DB schema — `docs/api.yaml` is the OpenAPI 3.0 spec
- No duplicate business logic between routes and services; routes delegate to `api_service.py`
- No secrets committed to the repo; use `.env` (gitignored)
