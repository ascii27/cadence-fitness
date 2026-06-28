"""Eva state endpoint: adherence summary for the remote agent."""
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_eva
from ..db import get_db
from ..models import SessionLog
from ..schemas import StateOut
from ..services import streaks
from ..services.derive import get_current_routine, today_date

router = APIRouter(prefix="/api/state", tags=["state"])


@router.get("", response_model=StateOut)
async def state(_: bool = Depends(require_eva), db: Session = Depends(get_db)) -> StateOut:
    routine = get_current_routine(db)
    logs = db.execute(select(SessionLog)).scalars().all()
    planned = streaks.planned_days(routine)
    statuses = streaks.status_by_date(logs)
    today = today_date()

    last_log_date = max((log.session_date for log in logs), default=None)

    window_start = today - timedelta(days=30)
    planned_30 = 0
    completed_30 = 0
    d = window_start
    while d <= today:
        dow = d.strftime("%A").lower()
        if dow in planned:
            planned_30 += 1
            if statuses.get(d.isoformat()) in {"completed", "partial"}:
                completed_30 += 1
        d += timedelta(days=1)

    return StateOut(
        routine_version=routine.version if routine else 0,
        last_log_date=last_log_date,
        adherence_30d={
            "planned": planned_30,
            "completed": completed_30,
            "current_streak": streaks.compute_current_streak(planned, statuses, today),
        },
    )
