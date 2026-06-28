"""Adherence endpoint: current/longest streak + weekly summary."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_user
from ..db import get_db
from ..models import SessionLog
from ..schemas import AdherenceOut, WeeklySummary
from ..services import streaks
from ..services.derive import get_current_routine, today_date

router = APIRouter(prefix="/api/adherence", tags=["adherence"])


@router.get("", response_model=AdherenceOut)
async def adherence(_: str = Depends(require_user), db: Session = Depends(get_db)) -> AdherenceOut:
    routine = get_current_routine(db)
    logs = db.execute(select(SessionLog)).scalars().all()
    planned = streaks.planned_days(routine)
    statuses = streaks.status_by_date(logs)
    today = today_date()

    current = streaks.compute_current_streak(planned, statuses, today)
    if logs:
        start = min(streaks.parse(log.session_date) for log in logs)
    else:
        start = today
    longest = streaks.compute_longest_streak(planned, statuses, start, today)
    weeks = [WeeklySummary(**w) for w in streaks.weekly_summary(planned, statuses, today)]
    return AdherenceOut(current_streak=current, longest_streak=longest, weeks=weeks)
