"""Adherence math: streaks, weekly summaries, milestone detection."""
from __future__ import annotations

from datetime import date, timedelta

from ..models import Routine, SessionLog

MILESTONES = (7, 14, 30)
_GOOD = {"completed", "partial"}


def iso(d: date) -> str:
    return d.isoformat()


def parse(d: str) -> date:
    return date.fromisoformat(d)


def planned_days(routine: Routine | None) -> set[str]:
    if routine is None:
        return set()
    return {
        day.get("day_of_week")
        for day in routine.days
        if day.get("session_type") != "rest"
    }


def status_by_date(logs: list[SessionLog]) -> dict[str, str | None]:
    """Most recent log per date wins."""
    out: dict[str, str | None] = {}
    for log in sorted(logs, key=lambda x: x.logged_at):
        out[log.session_date] = log.status
    return out


def compute_current_streak(
    planned: set[str],
    statuses: dict[str, str | None],
    today: date,
) -> int:
    """Consecutive planned days completed/partial, walking back from today.

    Rest days are skipped (neither count nor break). Today gets grace: if it's a
    planned day with no log yet, the day isn't over, so it doesn't break the streak.
    """
    if not planned:
        return 0
    streak = 0
    d = today
    # Bound the walk so a misconfigured routine can't loop forever.
    for _ in range(366):
        dow = d.strftime("%A").lower()
        if dow in planned:
            status = statuses.get(iso(d))
            if status in _GOOD:
                streak += 1
            elif status is None and d == today:
                pass  # grace for an unlogged today
            else:
                break
        d -= timedelta(days=1)
    return streak


def compute_longest_streak(
    planned: set[str],
    statuses: dict[str, str | None],
    start: date,
    today: date,
) -> int:
    """Scan forward from start to today; longest run of completed/partial planned days."""
    if not planned or start > today:
        return 0
    longest = 0
    run = 0
    d = start
    while d <= today:
        dow = d.strftime("%A").lower()
        if dow in planned:
            status = statuses.get(iso(d))
            if status in _GOOD:
                run += 1
                longest = max(longest, run)
            elif status is None and d == today:
                pass  # grace for today; do not reset
            else:
                run = 0
        d += timedelta(days=1)
    return longest


def week_start(d: date) -> date:
    """Monday-based week start."""
    return d - timedelta(days=d.weekday())


def weekly_summary(
    planned: set[str],
    statuses: dict[str, str | None],
    today: date,
    weeks: int = 12,
) -> list[dict]:
    """Planned vs completed counts per week for the last `weeks` weeks."""
    current_week_start = week_start(today)
    out: list[dict] = []
    for i in range(weeks - 1, -1, -1):
        ws = current_week_start - timedelta(weeks=i)
        planned_count = 0
        completed_count = 0
        for offset in range(7):
            d = ws + timedelta(days=offset)
            if d > today:
                continue
            dow = d.strftime("%A").lower()
            if dow in planned:
                planned_count += 1
                if statuses.get(iso(d)) in _GOOD:
                    completed_count += 1
        out.append({"week_start": iso(ws), "planned": planned_count, "completed": completed_count})
    return out


def milestone_hit(streak: int) -> int | None:
    """Return the milestone value if the streak exactly reached one, else None."""
    return streak if streak in MILESTONES else None
