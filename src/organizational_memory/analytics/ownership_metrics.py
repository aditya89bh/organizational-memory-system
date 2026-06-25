"""Ownership metrics.

Summarizes how organizational memory is distributed across owners: total records
per owner, open and overdue work per owner, decisions and risks per owner, and
how many owner-bearing records have no owner at all.
"""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.analytics.common import (
    count_by,
    is_open_status,
    is_overdue,
    owner_or_unassigned,
)
from organizational_memory.models import Decision, Risk
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

OWNER_TYPES = ("Decision", "Commitment", "Task", "OpenLoop", "Risk", "ActionItem")


@dataclass(frozen=True)
class OwnershipReport:
    """Aggregate ownership metrics across owner-bearing records."""

    records_by_owner: dict[str, int] = field(default_factory=dict)
    open_by_owner: dict[str, int] = field(default_factory=dict)
    overdue_by_owner: dict[str, int] = field(default_factory=dict)
    decisions_by_owner: dict[str, int] = field(default_factory=dict)
    risks_by_owner: dict[str, int] = field(default_factory=dict)
    unowned: int = 0


def _has_owner(record: BaseRecord) -> bool:
    return bool(getattr(record, "owner_id", None))


def ownership_metrics(
    store: MemoryStore,
    *,
    now: datetime | None = None,
) -> OwnershipReport:
    """Compute :class:`OwnershipReport` from owner-bearing records."""
    reference = now or utc_now()
    records: list[BaseRecord] = []
    for type_name in OWNER_TYPES:
        records.extend(store.list_records(type_name))

    owned = [record for record in records if _has_owner(record)]
    unowned = sum(1 for record in records if not _has_owner(record))

    open_owned = [
        record
        for record in owned
        if is_open_status(getattr(record, "status", "open"))
    ]
    overdue_owned = [record for record in owned if is_overdue(record, reference)]

    return OwnershipReport(
        records_by_owner=count_by(owned, owner_or_unassigned),
        open_by_owner=count_by(open_owned, owner_or_unassigned),
        overdue_by_owner=count_by(overdue_owned, owner_or_unassigned),
        decisions_by_owner=count_by(
            [r for r in owned if isinstance(r, Decision)], owner_or_unassigned
        ),
        risks_by_owner=count_by(
            [r for r in owned if isinstance(r, Risk)], owner_or_unassigned
        ),
        unowned=unowned,
    )
