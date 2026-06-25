"""Decision velocity metrics.

Summarizes how many decisions were made, when, by whom, and in which meetings,
plus a simple active-vs-superseded breakdown. All counts are deterministic.
"""

from dataclasses import dataclass, field

from organizational_memory.analytics.common import (
    count_by,
    iso_week,
    meeting_or_none,
    owner_or_unassigned,
)
from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.storage.store import MemoryStore


@dataclass(frozen=True)
class DecisionVelocityReport:
    """Aggregate decision velocity metrics."""

    total: int
    per_week: dict[str, int] = field(default_factory=dict)
    by_meeting: dict[str, int] = field(default_factory=dict)
    by_owner: dict[str, int] = field(default_factory=dict)
    active: int = 0
    superseded: int = 0


def _decisions(store: MemoryStore) -> list[Decision]:
    return [r for r in store.list_records("Decision") if isinstance(r, Decision)]


def decision_velocity(store: MemoryStore) -> DecisionVelocityReport:
    """Compute :class:`DecisionVelocityReport` from stored decisions.

    Decisions are bucketed by ISO week using ``decided_at`` when available and
    ``created_at`` otherwise. ``active`` counts proposed/accepted decisions;
    ``superseded`` counts superseded ones.
    """
    decisions = _decisions(store)
    per_week = count_by(
        decisions, lambda d: iso_week(d.decided_at or d.created_at)
    )
    by_meeting = count_by(decisions, meeting_or_none)
    by_owner = count_by(decisions, owner_or_unassigned)
    active = sum(
        1
        for d in decisions
        if d.status in (DecisionStatus.PROPOSED, DecisionStatus.ACCEPTED)
    )
    superseded = sum(
        1 for d in decisions if d.status is DecisionStatus.SUPERSEDED
    )
    return DecisionVelocityReport(
        total=len(decisions),
        per_week=per_week,
        by_meeting=by_meeting,
        by_owner=by_owner,
        active=active,
        superseded=superseded,
    )
