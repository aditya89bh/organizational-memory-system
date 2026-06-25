"""Shared helpers for deterministic workflow analytics.

These utilities keep the analytics modules small and consistent: grouping and
counting, ISO-week bucketing, and shared status vocabularies. Everything here is
deterministic and side-effect free.
"""

from collections.abc import Callable, Iterable
from datetime import datetime
from enum import Enum
from typing import TypeVar

from organizational_memory.schemas.base import BaseRecord

T = TypeVar("T")

UNASSIGNED = "unassigned"
NO_MEETING = "none"

# Status values that mean a record is finished and needs no further action.
TERMINAL_STATUSES = frozenset(
    {
        "completed",
        "done",
        "resolved",
        "closed",
        "cancelled",
        "dismissed",
        "mitigated",
        "rejected",
        "superseded",
        "accepted",
    }
)

# Status values that mean a record is still active / needs attention.
OPEN_STATUSES = frozenset(
    {
        "pending",
        "in_progress",
        "blocked",
        "todo",
        "open",
        "proposed",
        "identified",
    }
)


def status_value(status: object) -> str:
    """Return the comparable string value of a status enum or string."""
    return status.value if isinstance(status, Enum) else str(status)


def is_open_status(status: object) -> bool:
    """Return whether ``status`` represents active, unfinished work."""
    return status_value(status) not in TERMINAL_STATUSES


def count_by(items: Iterable[T], key: Callable[[T], str]) -> dict[str, int]:
    """Return a count of ``items`` grouped by ``key``, sorted by key."""
    counts: dict[str, int] = {}
    for item in items:
        bucket = key(item)
        counts[bucket] = counts.get(bucket, 0) + 1
    return dict(sorted(counts.items()))


def iso_week(moment: datetime) -> str:
    """Return the ISO week label (``YYYY-Www``) for ``moment``."""
    year, week, _ = moment.isocalendar()
    return f"{year:04d}-W{week:02d}"


def iso_date(moment: datetime) -> str:
    """Return the ISO calendar date (``YYYY-MM-DD``) for ``moment``."""
    return moment.date().isoformat()


def owner_or_unassigned(record: BaseRecord) -> str:
    """Return a record's owner id, or :data:`UNASSIGNED` when absent."""
    owner = getattr(record, "owner_id", None)
    return owner if owner else UNASSIGNED


def meeting_or_none(record: BaseRecord) -> str:
    """Return a record's source meeting id, or :data:`NO_MEETING` when absent."""
    meeting = getattr(record, "source_meeting_id", None)
    return meeting if meeting else NO_MEETING


def safe_ratio(numerator: int, denominator: int) -> float:
    """Return ``numerator / denominator`` rounded, or ``0.0`` when empty."""
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def is_overdue(record: BaseRecord, now: datetime) -> bool:
    """Return whether ``record`` has a past due date and is still open.

    Records without a ``due_at`` are never overdue, and records in a terminal
    status are excluded even if their due date has passed.
    """
    due_at = getattr(record, "due_at", None)
    if not isinstance(due_at, datetime) or due_at >= now:
        return False
    status = getattr(record, "status", None)
    return status is None or is_open_status(status)


def days_overdue(record: BaseRecord, now: datetime) -> float:
    """Return how many days past due ``record`` is, or ``0.0`` if not overdue."""
    due_at = getattr(record, "due_at", None)
    if not isinstance(due_at, datetime) or due_at >= now:
        return 0.0
    return round((now - due_at).total_seconds() / 86400.0, 6)
