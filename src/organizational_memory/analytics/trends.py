"""Trend analysis across weekly time buckets.

Produces deterministic weekly counts for decisions, commitments, open loops, and
overdue items, along with the change from the previous populated bucket. Weeks
use ISO week labels (``YYYY-Www``).
"""

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.analytics.common import is_overdue, iso_week
from organizational_memory.models import Commitment, Decision, OpenLoop
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now


@dataclass(frozen=True)
class TrendPoint:
    """A single time bucket with its count and change from the previous one."""

    bucket: str
    count: int
    change: int


@dataclass(frozen=True)
class TrendReport:
    """Weekly trend series for the core record types."""

    decisions: list[TrendPoint] = field(default_factory=list)
    commitments: list[TrendPoint] = field(default_factory=list)
    open_loops: list[TrendPoint] = field(default_factory=list)
    overdue: list[TrendPoint] = field(default_factory=list)


def _weekly_series(moments: Iterable[datetime]) -> list[TrendPoint]:
    counts: dict[str, int] = {}
    for moment in moments:
        bucket = iso_week(moment)
        counts[bucket] = counts.get(bucket, 0) + 1
    points: list[TrendPoint] = []
    previous = 0
    for bucket in sorted(counts):
        count = counts[bucket]
        points.append(TrendPoint(bucket=bucket, count=count, change=count - previous))
        previous = count
    return points


def trends(store: MemoryStore, *, now: datetime | None = None) -> TrendReport:
    """Compute :class:`TrendReport` with weekly counts and deltas."""
    reference = now or utc_now()

    decisions = [r for r in store.list_records("Decision") if isinstance(r, Decision)]
    commitments = [
        r for r in store.list_records("Commitment") if isinstance(r, Commitment)
    ]
    open_loops = [r for r in store.list_records("OpenLoop") if isinstance(r, OpenLoop)]

    overdue_moments: list[datetime] = []
    for type_name in ("Task", "Commitment", "OpenLoop"):
        for record in store.list_records(type_name):
            if is_overdue(record, reference):
                due_at = getattr(record, "due_at", None)
                if isinstance(due_at, datetime):
                    overdue_moments.append(due_at)

    def _record_moment(record: BaseRecord) -> datetime:
        decided = getattr(record, "decided_at", None)
        return decided if isinstance(decided, datetime) else record.created_at

    return TrendReport(
        decisions=_weekly_series(_record_moment(d) for d in decisions),
        commitments=_weekly_series(c.created_at for c in commitments),
        open_loops=_weekly_series(loop.created_at for loop in open_loops),
        overdue=_weekly_series(overdue_moments),
    )
