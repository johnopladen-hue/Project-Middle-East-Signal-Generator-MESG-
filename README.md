# Project-Middle-East-Signal-Generator-MESG-

## Local development

One-time setup:

```
cd backend && python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
cd frontend && npm install
```

Seed synthetic dev data (idempotent; pass `--reset` to wipe and reseed) - see `backend/app/dev_seed.py`:

```
cd backend && ..\backend\.venv\Scripts\python -m app.dev_seed
```

Run both backend and frontend with one command (see `scripts/dev.py`):

```
backend\.venv\Scripts\python scripts\dev.py
```

- Backend: http://127.0.0.1:8000/health
- Frontend: http://127.0.0.1:5173/ (log in as `analyst` / `correct-password` — a dev-only seeded account, see `backend/app/database.py`)

**Local dev database:** SQLite, a real file at `backend/mesg_dev.db` (`MESG_DATABASE_URL`, default `sqlite:///./mesg_dev.db` - see `backend/app/database.py`). Production is planned as PostgreSQL ([D-009](documents/decisions/D-009-v1-technology-stack.md)); the self-contained pytest suite uses its own isolated temp-file SQLite per run (`backend/tests/conftest.py`), never this dev file. This dev/prod database divergence is a known, accepted risk while Postgres isn't yet stood up - see `documents/architecture.md`.

Hosting/deploy: localhost is the development environment only, not an automated deploy target - see [D-011](documents/decisions/D-011-hosting-platform-and-deploy-mechanism.md).
