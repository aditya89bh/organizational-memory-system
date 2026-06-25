"""Organizational bottleneck metrics.

Combines other analytics into deterministic bottleneck signals: owners carrying
heavy overdue load, recurring unresolved questions, records blocked by
dependencies, and meetings that generate many open loops but few decisions.
"""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.analytics.dependency_analytics import dependency_analytics
from organizational_memory.analytics.meeting_effectiveness import (
    meeting_effectiveness,
)
from organizational_memory.analytics.overdue_tasks import overdue_tasks
from organizational_memory.analytics.repeated_discussions import (
    RepeatedCluster,
    repeated_discussions,
)
from organizational_memory.storage.store import MemoryStore

DEFAULT_OVERDUE_THRESHOLD = 2
DEFAULT_MIN_OPEN_LOOPS = 2
DEFAULT_MAX_DECISIONS = 0


@dataclass(frozen=True)
class LowSignalMeeting:
    """A meeting producing many open loops but few decisions."""

    meeting_id: str
    open_loops: int
    decisions: int


@dataclass(frozen=True)
class BottleneckReport:
    """Aggregate bottleneck signals across the organization."""

    overloaded_owners: dict[str, int] = field(default_factory=dict)
    recurring_unresolved: list[RepeatedCluster] = field(default_factory=list)
    blocked_records: tuple[str, ...] = ()
    multi_blockers: dict[str, int] = field(default_factory=dict)
    low_signal_meetings: list[LowSignalMeeting] = field(default_factory=list)


def bottlenecks(
    store: MemoryStore,
    *,
    now: datetime | None = None,
    overdue_threshold: int = DEFAULT_OVERDUE_THRESHOLD,
    min_open_loops: int = DEFAULT_MIN_OPEN_LOOPS,
    max_decisions: int = DEFAULT_MAX_DECISIONS,
) -> BottleneckReport:
    """Compute :class:`BottleneckReport` by combining analytics signals."""
    overdue = overdue_tasks(store, now=now)
    overloaded = {
        owner: count
        for owner, count in overdue.by_owner.items()
        if count >= overdue_threshold
    }

    repeated = repeated_discussions(store)
    dependencies = dependency_analytics(store)
    effectiveness = meeting_effectiveness(store)

    low_signal = [
        LowSignalMeeting(
            meeting_id=meeting.meeting_id,
            open_loops=meeting.open_loops,
            decisions=meeting.decisions,
        )
        for meeting in effectiveness.meetings
        if meeting.open_loops >= min_open_loops and meeting.decisions <= max_decisions
    ]

    return BottleneckReport(
        overloaded_owners=dict(
            sorted(overloaded.items(), key=lambda item: (-item[1], item[0]))
        ),
        recurring_unresolved=repeated.open_loop_clusters,
        blocked_records=dependencies.blocked_records,
        multi_blockers=dependencies.multi_blockers,
        low_signal_meetings=low_signal,
    )
