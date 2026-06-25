"""Commitment completion metrics.

Summarizes how many commitments exist, how many are still open versus completed
or cancelled, the overall completion rate, and completion broken down by owner
and meeting.
"""

from dataclasses import dataclass, field

from organizational_memory.analytics.common import (
    count_by,
    meeting_or_none,
    owner_or_unassigned,
    safe_ratio,
)
from organizational_memory.models import Commitment
from organizational_memory.models.enums import CommitmentStatus
from organizational_memory.storage.store import MemoryStore


@dataclass(frozen=True)
class CommitmentCompletionReport:
    """Aggregate commitment completion metrics."""

    total: int
    open: int
    completed: int
    cancelled: int
    completion_rate: float
    completed_by_owner: dict[str, int] = field(default_factory=dict)
    completed_by_meeting: dict[str, int] = field(default_factory=dict)


def _commitments(store: MemoryStore) -> list[Commitment]:
    return [r for r in store.list_records("Commitment") if isinstance(r, Commitment)]


def commitment_completion(store: MemoryStore) -> CommitmentCompletionReport:
    """Compute :class:`CommitmentCompletionReport` from stored commitments.

    ``open`` counts pending and in-progress commitments; ``completion_rate`` is
    completed divided by total.
    """
    commitments = _commitments(store)
    completed = [c for c in commitments if c.status is CommitmentStatus.COMPLETED]
    cancelled = sum(
        1 for c in commitments if c.status is CommitmentStatus.CANCELLED
    )
    open_count = sum(
        1
        for c in commitments
        if c.status in (CommitmentStatus.PENDING, CommitmentStatus.IN_PROGRESS)
    )
    return CommitmentCompletionReport(
        total=len(commitments),
        open=open_count,
        completed=len(completed),
        cancelled=cancelled,
        completion_rate=safe_ratio(len(completed), len(commitments)),
        completed_by_owner=count_by(completed, owner_or_unassigned),
        completed_by_meeting=count_by(completed, meeting_or_none),
    )
