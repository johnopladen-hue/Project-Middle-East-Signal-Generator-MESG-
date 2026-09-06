"""Point every test run at an isolated temp SQLite file, set before any
test module can import app.database (which creates its engine at import
time) — Keel Principle 5: self-contained, never touching a real dev db."""

import os
import tempfile

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["MESG_DATABASE_URL"] = f"sqlite:///{_db_path}"
