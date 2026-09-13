"""FastAPI app entrypoint — TDD §7 (API surface, representative slice).

Only /auth/* and a health check are wired up in this first slice. The
remaining routes (briefs, stories, signals, admin) land once the data-store
and pipeline pieces behind them exist — see documents/test_plan.md for
what's covered so far.
"""

from __future__ import annotations

import os
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.database import SessionLocal, init_db, seed_dev_user
from app.geo.regions import seed_aor_memberships
from app.routers.auth import router as auth_router
from app.routers.briefs import router as briefs_router
from app.routers.admin import router as admin_router
from app.routers.frame_divergence import router as frame_divergence_router
from app.routers.geo import router as geo_router
from app.routers.organizations import router as organizations_router
from app.routers.pipeline import router as pipeline_router
from app.routers.recipients import router as recipients_router
from app.routers.regions import router as regions_router
from app.routers.signals import router as signals_router
from app.routers.stories import router as stories_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    seed_dev_user()
    with SessionLocal() as session:
        seed_aor_memberships(session)
    yield


app = FastAPI(title="MESG API", version="0.1.0", lifespan=lifespan)

# DEV NOTE: falls back to a random per-process key. Real secret handling
# (platform-provided, never in code) lands once the hosting decision is
# made (Keel Principle 4; documents/decisions.md open list).
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("MESG_SESSION_SECRET", secrets.token_hex(32)))

app.include_router(auth_router)
app.include_router(briefs_router)
app.include_router(admin_router)
app.include_router(frame_divergence_router)
app.include_router(geo_router)
app.include_router(organizations_router)
app.include_router(pipeline_router)
app.include_router(recipients_router)
app.include_router(regions_router)
app.include_router(signals_router)
app.include_router(stories_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
