"""Open loop metrics.

Summarizes unresolved questions: how many exist, how many are resolved, how old
the unresolved ones are, the oldest outstanding items, and breakdowns by owner
and meeting. Ages are measured against a supplied reference time for
reproducibility.
"""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.analytics.common import (
    count_by,
    meeting_or_none,
    owner_or_unassigned,
)
from organizational_memory.models import OpenLoop
from organizational_memory.models.enums import OpenLoopStatus
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

DEFAULT_OLDEST_LIMIT = 5


@dataclass(frozen=True)
class OpenLoopAge:
    """An unresolved open loop and its age in days."""

    id: str
    question: str
    age_days: float


@dataclass(frozen=True)
class OpenLoopReport:
    """Aggregate open loop metrics."""

    total: int
    unresolved: int
    resolved: int
    average_age_days: float
    oldest_unresolved: list[OpenLoopAge] = field(default_factory=list)
    by_owner: dict[str, int] = field(default_factory=dict)
    by_meeting: dict[str, int] = field(default_factory=dict)


def _open_loops(store: MemoryStore) -> list[OpenLoop]:
    return [r for r in store.list_records("OpenLoop") if isinstance(r, OpenLoop)]


def _age_days(moment: datetime, now: datetime) -> float:
    return round(max(0.0, (now - moment).total_seconds() / 86400.0), 6)


def open_loop_metrics(
    store: MemoryStore,
    *,
    now: datetime | None = None,
    oldest_limit: int = DEFAULT_OLDEST_LIMIT,
) -> OpenLoopReport:
    """Compute :class:`OpenLoopReport` from stored open loops."""
    reference = now or utc_now()
    loops = _open_loops(store)
    unresolved = [loop for loop in loops if loop.status is OpenLoopStatus.OPEN]
    resolved = sum(1 for loop in loops if loop.status is OpenLoopStatus.RESOLVED)

    ages = [
        OpenLoopAge(
            id=loop.id,
            question=loop.question,
            age_days=_age_days(loop.created_at, reference),
        )
        for loop in unresolved
    ]
    average_age = (
        round(sum(age.age_days for age in ages) / len(ages), 6) if ages else 0.0
    )
    oldest = sorted(ages, key=lambda age: (-age.age_days, age.id))[:oldest_limit]

    return OpenLoopReport(
        total=len(loops),
        unresolved=len(unresolved),
        resolved=resolved,
        average_age_days=average_age,
        oldest_unresolved=oldest,
        by_owner=count_by(loops, owner_or_unassigned),
        by_meeting=count_by(loops, meeting_or_none),
    )
