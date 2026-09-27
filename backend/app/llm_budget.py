"""LLM spend ledger and budget circuit breaker (D-016, O-2).

Every Claude API call is estimated against this breaker before it happens.
A refusal is visible ("budget exhausted: N items not deep-analysed"), never
a silent drop (Keel Principle 11 - the same posture as Designation's
unmatched-pending-match). An unknown spend state - the ledger can't be
read - is treated as exhausted, not as zero: failing open would silently
blow past the Owner's $20/month cap (D-016), and a refusal that turns out
to be unnecessary costs nothing, while an allowed call that turns out to
be uncapped costs real money.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import LlmSpend, Settings

DEFAULT_MONTHLY_CAP_USD = 20.0
DEFAULT_DAILY_CAP_USD = DEFAULT_MONTHLY_CAP_USD / 30


@dataclass
class BudgetDecision:
    allowed: bool
    reason: str | None = None
    daily_spend_usd: float | None = None
    monthly_spend_usd: float | None = None


def _period_starts(now: datetime) -> tuple[datetime, datetime]:
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = day_start.replace(day=1)
    return day_start, month_start


def caps(db: Session) -> tuple[float, float]:
    """Return (daily cap, monthly cap) in USD, from Settings or the defaults."""
    settings = db.query(Settings).filter_by(id=1).first()
    values = settings.values if settings else {}
    daily = values.get("llm_daily_cap_usd", DEFAULT_DAILY_CAP_USD)
    monthly = values.get("llm_monthly_cap_usd", DEFAULT_MONTHLY_CAP_USD)
    return float(daily), float(monthly)


def _spend_since(db: Session, since: datetime) -> float:
    total = db.query(func.sum(LlmSpend.cost_usd)).filter(LlmSpend.created_at >= since).scalar()
    return float(total or 0.0)


def current_spend(db: Session) -> tuple[float, float]:
    """Return (spend today, spend this month), in USD. Raises if the
    ledger can't be read - callers that need a fail-closed result should
    go through check_budget, not call this directly."""
    day_start, month_start = _period_starts(datetime.now(timezone.utc))
    return _spend_since(db, day_start), _spend_since(db, month_start)


def check_budget(db: Session, estimated_cost_usd: float) -> BudgetDecision:
    """Call before every Claude API call with the call's estimated cost.
    Refuses if that estimate would push today's or this month's ledgered
    spend over its cap - or if spend can't be determined at all."""
    try:
        daily_cap, monthly_cap = caps(db)
        daily_spend, monthly_spend = current_spend(db)
    except Exception:
        return BudgetDecision(allowed=False, reason="budget exhausted: spend state unknown")

    if daily_spend + estimated_cost_usd > daily_cap:
        return BudgetDecision(
            allowed=False,
            reason=f"budget exhausted: daily cap ${daily_cap:.2f} reached",
            daily_spend_usd=daily_spend,
            monthly_spend_usd=monthly_spend,
        )
    if monthly_spend + estimated_cost_usd > monthly_cap:
        return BudgetDecision(
            allowed=False,
            reason=f"budget exhausted: monthly cap ${monthly_cap:.2f} reached",
            daily_spend_usd=daily_spend,
            monthly_spend_usd=monthly_spend,
        )
    return BudgetDecision(allowed=True, daily_spend_usd=daily_spend, monthly_spend_usd=monthly_spend)


def record_spend(
    db: Session,
    *,
    model: str,
    purpose: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
) -> LlmSpend:
    """Ledger a call that actually happened. Called after the API responds,
    with its real token counts - never estimated (estimates only gate
    check_budget's decision, they never substitute for a real cost)."""
    entry = LlmSpend(
        model=model,
        purpose=purpose,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost_usd,
    )
    db.add(entry)
    db.commit()
    return entry
