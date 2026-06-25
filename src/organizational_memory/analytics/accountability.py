"""Accountability metrics.

Measures how work is assigned and followed through: assigned versus unassigned
work, a per-owner follow-through score derived from completed/open/overdue
counts, unresolved load per owner, commitments missing due dates, and tasks
missing owners.
"""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.analytics.common import (
    count_by,
    is_open_status,
    is_overdue,
    owner_or_unassigned,
    safe_ratio,
    status_value,
)
from organizational_memory.models import Commitment, Task
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

WORK_TYPES = ("Task", "Commitment", "OpenLoop", "ActionItem")
COMPLETED_STATUSES = frozenset({"completed", "done", "resolved"})


@dataclass(frozen=True)
class OwnerAccountability:
    """Per-owner accountability breakdown."""

    owner: str
    assigned: int
    completed: int
    open: int
    overdue: int
    follow_through_score: float


@dataclass(frozen=True)
class AccountabilityReport:
    """Aggregate accountability metrics."""

    assigned: int
    unassigned: int
    owners: list[OwnerAccountability] = field(default_factory=list)
    unresolved_by_owner: dict[str, int] = field(default_factory=dict)
    commitments_without_due_date: int = 0
    tasks_without_owner: int = 0


def _has_owner(record: BaseRecord) -> bool:
    return bool(getattr(record, "owner_id", None))


def _is_completed(record: BaseRecord) -> bool:
    status = getattr(record, "status", None)
    return status is not None and status_value(status) in COMPLETED_STATUSES


def accountability(
    store: MemoryStore,
    *,
    now: datetime | None = None,
) -> AccountabilityReport:
    """Compute :class:`AccountabilityReport` from work records."""
    reference = now or utc_now()
    records: list[BaseRecord] = []
    for type_name in WORK_TYPES:
        records.extend(store.list_records(type_name))

    owned = [record for record in records if _has_owner(record)]
    unassigned = sum(1 for record in records if not _has_owner(record))

    owners_seen = sorted({owner_or_unassigned(record) for record in owned})
    owner_rows: list[OwnerAccountability] = []
    for owner in owners_seen:
        items = [r for r in owned if owner_or_unassigned(r) == owner]
        completed = sum(1 for r in items if _is_completed(r))
        open_count = sum(
            1 for r in items if is_open_status(getattr(r, "status", "open"))
        )
        overdue = sum(1 for r in items if is_overdue(r, reference))
        owner_rows.append(
            OwnerAccountability(
                owner=owner,
                assigned=len(items),
                completed=completed,
                open=open_count,
                overdue=overdue,
                follow_through_score=safe_ratio(completed, completed + open_count),
            )
        )

    open_owned = [
        r for r in owned if is_open_status(getattr(r, "status", "open"))
    ]

    commitments_without_due = sum(
        1
        for r in store.list_records("Commitment")
        if isinstance(r, Commitment) and r.due_at is None
    )
    tasks_without_owner = sum(
        1
        for r in store.list_records("Task")
        if isinstance(r, Task) and not r.owner_id
    )

    return AccountabilityReport(
        assigned=len(owned),
        unassigned=unassigned,
        owners=owner_rows,
        unresolved_by_owner=count_by(open_owned, owner_or_unassigned),
        commitments_without_due_date=commitments_without_due,
        tasks_without_owner=tasks_without_owner,
    )
