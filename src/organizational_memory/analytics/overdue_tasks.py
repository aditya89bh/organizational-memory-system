"""Overdue work metrics.

Identifies tasks, commitments, and open loops whose due date has passed while
they remain open, with breakdowns by owner and meeting and the number of days
each item is overdue. Overdue status is evaluated against a supplied reference
time for reproducibility.
"""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.analytics.common import (
    count_by,
    days_overdue,
    is_overdue,
    meeting_or_none,
    owner_or_unassigned,
)
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

_OVERDUE_TYPES = ("Task", "Commitment", "OpenLoop")


@dataclass(frozen=True)
class OverdueItem:
    """A single overdue record and how far past due it is."""

    id: str
    record_type: str
    owner: str
    source_meeting: str
    days_overdue: float


@dataclass(frozen=True)
class OverdueReport:
    """Aggregate overdue work metrics."""

    total: int
    tasks: int
    commitments: int
    open_loops: int
    by_owner: dict[str, int] = field(default_factory=dict)
    by_meeting: dict[str, int] = field(default_factory=dict)
    items: list[OverdueItem] = field(default_factory=list)


def _overdue_records(store: MemoryStore, now: datetime) -> list[BaseRecord]:
    records: list[BaseRecord] = []
    for type_name in _OVERDUE_TYPES:
        records.extend(
            record
            for record in store.list_records(type_name)
            if is_overdue(record, now)
        )
    return records


def overdue_tasks(
    store: MemoryStore,
    *,
    now: datetime | None = None,
) -> OverdueReport:
    """Compute :class:`OverdueReport` from stored tasks, commitments, loops."""
    reference = now or utc_now()
    records = _overdue_records(store, reference)
    items = [
        OverdueItem(
            id=record.id,
            record_type=type(record).__name__,
            owner=owner_or_unassigned(record),
            source_meeting=meeting_or_none(record),
            days_overdue=days_overdue(record, reference),
        )
        for record in records
    ]
    items.sort(key=lambda item: (-item.days_overdue, item.id))

    def _count(type_name: str) -> int:
        return sum(1 for item in items if item.record_type == type_name)

    return OverdueReport(
        total=len(items),
        tasks=_count("Task"),
        commitments=_count("Commitment"),
        open_loops=_count("OpenLoop"),
        by_owner=count_by(records, owner_or_unassigned),
        by_meeting=count_by(records, meeting_or_none),
        items=items,
    )
