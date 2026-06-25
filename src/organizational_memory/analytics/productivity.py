"""Productivity metrics.

Conservative, structural indicators derived purely from record status and
counts: the ratio of closed to open work, structured outputs per meeting, and
completed commitments per week. These describe the shape of the recorded memory
and are not measures of real productivity or employee performance.
"""

from dataclasses import dataclass, field

from organizational_memory.analytics.common import (
    count_by,
    is_open_status,
    iso_week,
    safe_ratio,
)
from organizational_memory.models import Commitment
from organizational_memory.models.enums import CommitmentStatus
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore

WORK_TYPES = ("Task", "Commitment", "OpenLoop", "ActionItem")
STRUCTURED_TYPES = ("Decision", "Commitment", "Task", "OpenLoop", "Risk")


@dataclass(frozen=True)
class ProductivityReport:
    """Conservative, deterministic productivity indicators."""

    total_work: int
    closed_work: int
    open_work: int
    closed_work_ratio: float
    unresolved_work_ratio: float
    structured_outputs_per_meeting: float
    completed_commitments_per_week: dict[str, int] = field(default_factory=dict)


def productivity(store: MemoryStore) -> ProductivityReport:
    """Compute :class:`ProductivityReport` from stored records."""
    work: list[BaseRecord] = []
    for type_name in WORK_TYPES:
        work.extend(store.list_records(type_name))

    open_work = sum(
        1 for r in work if is_open_status(getattr(r, "status", "open"))
    )
    closed_work = len(work) - open_work

    structured = sum(
        len(store.list_records(type_name)) for type_name in STRUCTURED_TYPES
    )
    meeting_count = len(store.list_records("Meeting"))

    completed_commitments = [
        r
        for r in store.list_records("Commitment")
        if isinstance(r, Commitment) and r.status is CommitmentStatus.COMPLETED
    ]
    completed_per_week = count_by(
        completed_commitments, lambda c: iso_week(c.created_at)
    )

    return ProductivityReport(
        total_work=len(work),
        closed_work=closed_work,
        open_work=open_work,
        closed_work_ratio=safe_ratio(closed_work, len(work)),
        unresolved_work_ratio=safe_ratio(open_work, len(work)),
        structured_outputs_per_meeting=safe_ratio(structured, meeting_count),
        completed_commitments_per_week=completed_per_week,
    )
