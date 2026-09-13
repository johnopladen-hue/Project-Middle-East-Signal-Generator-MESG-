"""One-command local dev run (D-011, first article O-2).

Starts the FastAPI backend (uvicorn, port 8000) and the Vite frontend dev
server (port 5173, proxying /api to the backend - see frontend/vite.config.js)
as child processes, streaming both logs prefixed by name. Ctrl+C stops both.

Prerequisite (one-time): backend deps installed into a venv, frontend deps
installed via npm - see README.md "Local development" for the exact steps.

Usage (from the repo root, with backend/.venv active or on PATH):
    python scripts/dev.py
"""

from __future__ import annotations

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
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(BACKEND_DIR),
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
