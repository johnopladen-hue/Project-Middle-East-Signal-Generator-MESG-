"""SQLite for local dev; PostgreSQL in production (D-009). SQLAlchemy is the
swap boundary, so nothing above this module needs to know which one is live."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.models import Base, User

DATABASE_URL = os.environ.get("MESG_DATABASE_URL", "sqlite:///./mesg_dev.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_dev_user() -> None:
    """DEV SEED ONLY — a throwaway local account, not a real credential.

    Real user provisioning is out of scope until the auth mechanism is
    exercised against a real deploy; see documents/decisions.md.
    """
    with SessionLocal() as session:
        if session.query(User).filter_by(username="analyst").first():
            return
        session.add(
            User(
                username="analyst",
                password_hash=hash_password("correct-password"),
                role="admin",
                active=True,
            )
        )
        session.commit()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
