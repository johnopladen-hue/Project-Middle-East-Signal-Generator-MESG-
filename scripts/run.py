r"""Daily-use launcher: MESG collecting on its own (U-3, D-019 scheduler & runtime).

The same two processes as scripts/dev.py - FastAPI backend on port 8000 and
the Vite frontend on 5173 - with two differences:

  * the backend runs WITH the scheduler (MESG_SCHEDULER=1): RSS every 30 min,
    Telegram every 15 min, NLLB triage translation every 5 min, catching up
    at once on anything missed while the PC was off;
  * the backend runs WITHOUT --reload, so a code edit never restarts it in
    the middle of a collection run.

Use scripts/dev.py for development (reload on, no scheduler). Only one
scheduler can run per checkout: a second one refuses to start
(backend/data/scheduler.lock) and says so in the log.

Usage (from the repo root):
    backend\.venv\Scripts\python scripts\run.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
FRONTEND_DIR = REPO_ROOT / "frontend"


def _stream(proc: subprocess.Popen, prefix: str) -> None:
    for line in proc.stdout:
        print(f"[{prefix}] {line}", end="")


def main() -> None:
    npm = shutil.which("npm")
    if npm is None:
        print("npm not found on PATH; install Node.js first.", file=sys.stderr)
        raise SystemExit(1)

    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(BACKEND_DIR),
        env={**os.environ, "MESG_SCHEDULER": "1", "PYTHONUNBUFFERED": "1"},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    frontend = subprocess.Popen(
        [npm, "run", "dev"],
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    threads = [
        threading.Thread(target=_stream, args=(backend, "backend"), daemon=True),
        threading.Thread(target=_stream, args=(frontend, "frontend"), daemon=True),
    ]
    for t in threads:
        t.start()

    print("backend:  http://127.0.0.1:8000/health")
    print("frontend: http://127.0.0.1:5173/  (Ctrl+C to stop both)")
    print("scheduler: on - rss 30 min, telegram 15 min, translate 5 min (see the [scheduler] lines)")

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for proc in (backend, frontend):
            if proc.poll() is None:
                proc.terminate()


if __name__ == "__main__":
    main()
