"""Auth endpoints — TDD §7, §10. Session-cookie auth (D-009/F-3): the
session id is the only thing in the cookie; the server holds the state."""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import verify_password
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60
_failed_attempts: dict[str, list[float]] = defaultdict(list)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    active: bool

    model_config = {"from_attributes": True}


def _rate_limit_check(username: str) -> None:
    now = time.time()
    attempts = [t for t in _failed_attempts[username] if now - t < WINDOW_SECONDS]
    _failed_attempts[username] = attempts
    if len(attempts) >= MAX_ATTEMPTS:
        retry_after = int(WINDOW_SECONDS - (now - attempts[0])) + 1
        raise HTTPException(
            status_code=429,
            detail="Too many attempts",
            headers={"Retry-After": str(retry_after)},
        )


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    _rate_limit_check(payload.username)

    user = db.query(User).filter_by(username=payload.username, active=True).first()
    if not user or not verify_password(payload.password, user.password_hash):
        _failed_attempts[payload.username].append(time.time())
        raise HTTPException(status_code=401, detail="Incorrect username or password.")

    _failed_attempts.pop(payload.username, None)
    request.session["user_id"] = user.id
    return user


@router.post("/logout", status_code=204)
def logout(request: Request):
    request.session.clear()
    return Response(status_code=204)


@router.get("/me", response_model=UserOut)
def me(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(User).filter_by(id=user_id, active=True).first()
    if not user:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
