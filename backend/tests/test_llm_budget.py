"""LLM budget circuit breaker tests (D-016, O-2). Self-contained, isolated
temp SQLite (Keel Principle 5)."""

from __future__ import annotations

from app.database import SessionLocal, engine, init_db
from app.llm_budget import check_budget, current_spend, record_spend
from app.models import LlmSpend, Settings

init_db()


def _set_caps(daily_usd: float | None = None, monthly_usd: float | None = None) -> None:
    with SessionLocal() as session:
        settings = session.query(Settings).filter_by(id=1).first()
        if settings is None:
            settings = Settings(id=1, values={})
            session.add(settings)
        values = dict(settings.values)
        if daily_usd is not None:
            values["llm_daily_cap_usd"] = daily_usd
        if monthly_usd is not None:
            values["llm_monthly_cap_usd"] = monthly_usd
        settings.values = values
        session.commit()


def test_allows_a_call_under_the_default_caps():
    _set_caps(daily_usd=20.0, monthly_usd=20.0)
    with SessionLocal() as session:
        decision = check_budget(session, estimated_cost_usd=0.01)
    assert decision.allowed is True
    assert decision.reason is None


def test_breaker_trips_when_the_estimate_would_exceed_the_monthly_cap():
    """Keel Principle 6 (prove it by tripping it): a call that fits under
    the default $20 cap is refused once the cap itself is set below what's
    already been spent — this is the same estimate, only the cap changed."""
    _set_caps(daily_usd=20.0, monthly_usd=20.0)
    with SessionLocal() as session:
        record_spend(session, model="claude-haiku-4-5", purpose="test", input_tokens=100, output_tokens=50, cost_usd=0.02)
        allowed_before = check_budget(session, estimated_cost_usd=0.01)
    assert allowed_before.allowed is True

    _set_caps(monthly_usd=0.02)  # already spent exactly this much
    with SessionLocal() as session:
        decision = check_budget(session, estimated_cost_usd=0.01)
    assert decision.allowed is False
    assert "monthly cap" in decision.reason


def test_breaker_trips_when_the_estimate_would_exceed_the_daily_cap():
    _set_caps(daily_usd=20.0, monthly_usd=20.0)
    with SessionLocal() as session:
        record_spend(session, model="claude-haiku-4-5", purpose="test", input_tokens=100, output_tokens=50, cost_usd=0.03)

    _set_caps(daily_usd=0.03, monthly_usd=20.0)
    with SessionLocal() as session:
        decision = check_budget(session, estimated_cost_usd=0.01)
    assert decision.allowed is False
    assert "daily cap" in decision.reason


def test_a_missing_ledger_blocks_calls_rather_than_allowing_them():
    """An unknown spend state - the ledger table itself unreadable - must
    fail closed, not open. Dropping and recreating the table proves the
    breaker doesn't quietly treat 'can't tell' as 'zero spent so far'."""
    _set_caps(daily_usd=20.0, monthly_usd=20.0)
    LlmSpend.__table__.drop(bind=engine)
    try:
        with SessionLocal() as session:
            decision = check_budget(session, estimated_cost_usd=0.01)
        assert decision.allowed is False
        assert decision.reason == "budget exhausted: spend state unknown"
    finally:
        LlmSpend.__table__.create(bind=engine)


def test_record_spend_persists_a_ledger_row_current_spend_reflects_it():
    with SessionLocal() as session:
        before_day, before_month = current_spend(session)
        record_spend(session, model="claude-haiku-4-5", purpose="triage-bakeoff", input_tokens=500, output_tokens=200, cost_usd=0.0035)
        after_day, after_month = current_spend(session)
    assert after_day == before_day + 0.0035
    assert after_month == before_month + 0.0035
