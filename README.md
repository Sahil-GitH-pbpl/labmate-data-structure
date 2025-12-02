# Hiccup System – Internal Staff System: Hiccup Module (V1.0)

Enterprise-grade FastAPI + React implementation for Dr. Bhasin's Lab to capture, triage, and resolve hiccups (process interruptions/errors) with RBAC, audit trails, WhatsApp notifications, and scheduler-driven reporting.

## Features
- JWT-based auth stub with roles (staff, hod, management, admin) and RBAC enforcement.
- Hiccup lifecycle: raise (with attachments), respond, management review/closure, escalate to NC, and follow-up tracking.
- SLA checks (response/closure overdue) surfaced in API and UI.
- Audit logs for all actions, confidential flag handling, and auto-generated hiccups API with internal token validation.
- Reports: daily digest, trend alerts, monthly learning digest, and simple dashboards.
- WhatsApp notification abstraction for creation + daily summary; APScheduler for cron jobs.
- Dockerized stack with MySQL 8, backend (gunicorn+uvicorn workers), frontend (React+nginx), and optional scheduler worker.

## Directory Layout
- `backend/` – FastAPI app (`app/main.py`), models, schemas, services, scheduler, and Alembic migrations.
- `frontend/` – Vite + React (TypeScript) SPA with dashboard, raise form, management views, and reports.
- `docker-compose.yml` – Local orchestration for MySQL, backend (7410), frontend (7411), and scheduler.

## Backend Setup (local)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.sample ../.env  # adjust values
alembic upgrade head
uvicorn app.main:app --reload --port 7410
```

## Frontend Setup (local)
```bash
cd frontend
npm install
npm run dev -- --port 7411
```

## Docker
1. Copy `.env.sample` to `.env` and update secrets (DB, JWT, WhatsApp, internal token).
2. Run `docker-compose up --build`.
3. Backend available at http://localhost:7410, frontend at http://localhost:7411.

Volumes:
- `mysql_data` for MySQL data
- `uploads` for attachments
- `logs` for backend/scheduler logs

## Environment Variables
See `.env.sample` for:
- DB_* for MySQL connectivity
- JWT_SECRET/JWT_ALGO for token validation
- WHATSAPP_API_URL/WHATSAPP_API_TOKEN for StewIndia integration
- MANAGEMENT_GROUP_NUMBERS (CSV)
- INTERNAL_TOKEN for auto-generate API
- TIMEZONE (default Asia/Kolkata)

## Key API Endpoints
- `POST /api/auth/token` – generate stub JWT.
- `POST /api/hiccups` – raise hiccup (multipart with attachment).
- `POST /api/hiccups/auto_generate` – internal auto-hiccup (X-Internal-Token).
- `GET /api/hiccups` / `GET /api/hiccups/{id}` – list/view with RBAC + SLA flags.
- `PATCH /api/hiccups/{id}/respond` – responder input.
- `PATCH /api/hiccups/{id}/status` – management close/escalate/under-review.
- `PATCH /api/hiccups/{id}/followup` – raiser follow-up after closure.
- `GET /api/reports/*` – daily digest, trends, monthly digest.

## Scheduler
APScheduler jobs (startup or `scheduler` service):
- Daily WhatsApp summary at 11:00 IST.
- Hourly SLA overdue check logs.
- 6-hourly follow-up due reminders.

## Security Notes
- JWT decoding via shared secret; replace with ARPRA JWT provider in production.
- File uploads validated for type/size and stored under `uploads/hiccups/<hiccup_id>/`.
- RBAC enforced server-side; confidential hiccups restricted to management/admin/raiser.

## Frontend Highlights
- Login stub to generate JWT.
- Dashboard showing counts and overdue items.
- Raise hiccup form with validation and attachment upload.
- Detail view with response/management/follow-up forms.
- Management board, reports dashboard, and placeholder settings for admin.

## Testing
- Run backend unit tests (if added) with `pytest` inside venv.
- Frontend build check: `npm run build`.
