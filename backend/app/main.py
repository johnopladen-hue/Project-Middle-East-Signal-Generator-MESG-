"""FastAPI app entrypoint — TDD §7 (API surface, representative slice).

Only /auth/* and a health check are wired up in this first slice. The
remaining routes (briefs, stories, signals, admin) land once the data-store
and pipeline pieces behind them exist — see documents/test_plan.md for
what's covered so far.
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="MESG API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
