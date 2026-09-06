"""FastAPI app entrypoint — TDD §7 (API surface, representative slice).

Only /auth/* and a health check are wired up in this first slice. The
remaining routes (briefs, stories, signals, admin) land once the data-store
and pipeline pieces behind them exist — see documents/test_plan.md for
what's covered so far.
"""

from __future__ import annotations

import os
import secrets

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.database import init_db, seed_dev_user
from app.routers.auth import router as auth_router

app = FastAPI(title="MESG API", version="0.1.0")

# DEV NOTE: falls back to a random per-process key. Real secret handling
# (platform-provided, never in code) lands once the hosting decision is
# made (Keel Principle 4; documents/decisions.md open list).
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("MESG_SESSION_SECRET", secrets.token_hex(32)))

app.include_router(auth_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_dev_user()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
