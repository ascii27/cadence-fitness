"""M1.7 — streak/adherence math (pure)."""
from __future__ import annotations

from datetime import date

from app.services import streaks

# Seed planned days: mon, wed, thu, fri, sat (tue/sun rest).
PLANNED = {"monday", "wednesday", "thursday", "friday", "saturday"}


def test_rest_day_does_not_break_streak():
    # Sat completed, Sun rest, Mon completed -> streak 2 counting back from Monday.
    statuses = {"2026-06-27": "completed", "2026-06-29": "completed"}  # Sat, Mon
    today = date(2026, 6, 29)  # Monday
    assert streaks.compute_current_streak(PLANNED, statuses, today) == 2


def test_today_unlogged_does_not_break():
    # Today (Mon) planned but unlogged; Sat completed -> streak counts Sat = 1.
    statuses = {"2026-06-27": "completed"}  # Sat
    today = date(2026, 6, 29)  # Monday, no log
    assert streaks.compute_current_streak(PLANNED, statuses, today) == 1


def test_missed_breaks_streak():
    statuses = {"2026-06-27": "missed", "2026-06-26": "completed"}  # Sat missed, Fri done
    today = date(2026, 6, 27)  # Saturday
    assert streaks.compute_current_streak(PLANNED, statuses, today) == 0


def test_partial_counts():
    statuses = {"2026-06-26": "partial"}  # Friday
    today = date(2026, 6, 26)
    assert streaks.compute_current_streak(PLANNED, statuses, today) == 1


def test_longest_streak():
    statuses = {
        "2026-06-22": "completed",  # Mon
        "2026-06-24": "completed",  # Wed
        "2026-06-25": "missed",     # Thu -> breaks
        "2026-06-26": "completed",  # Fri
        "2026-06-27": "completed",  # Sat
    }
    longest = streaks.compute_longest_streak(PLANNED, statuses, date(2026, 6, 22), date(2026, 6, 27))
    assert longest == 2


def test_milestone_hit():
    assert streaks.milestone_hit(7) == 7
    assert streaks.milestone_hit(14) == 14
    assert streaks.milestone_hit(30) == 30
    assert streaks.milestone_hit(6) is None
    assert streaks.milestone_hit(8) is None
