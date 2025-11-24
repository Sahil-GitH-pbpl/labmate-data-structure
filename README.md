# Infra HelpDesk

A FastAPI-based internal module for tracking infrastructure tickets with a lightweight vanilla JS frontend.

## Features
- Create tickets with optional photo upload
- IT/Admin workflows: pick, commit, update, resolve, mark invalid
- My/Department ticket views
- Delayed pick auto-flagging and daily email summary jobs
- Dockerized stack with MySQL

## Quick Start (Docker)
1. Copy `.env.example` to `.env` in `backend/` and adjust if needed.
2. Run `make up` to start backend, MySQL, and Adminer.
3. Apply migrations: `make migrate`.
4. Seed demo data: `make seed`.
5. Open http://localhost:8000 for UI, Swagger at http://localhost:8000/docs.

## Local Dev (venv)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./local.db
alembic upgrade head
uvicorn app.main:app --reload
```

## Auth
Use Bearer tokens that map to mock ARPRA JWTs:
- Staff: `alice`
- IT: `bob`
- Admin: `admin`

## Scripts
- `make fmt` – Black format
- `make lint` – Ruff lint
- `make test` – run pytest suite
- `make down` – stop containers

## Tests
Unit tests cover service rules and an API smoke flow.

## Screenshots
_Add screenshots here once captured._

## Future
Hook for V2 self-help suggestions is scaffolded via `V2_SELF_HELP_ENABLED` flag.
