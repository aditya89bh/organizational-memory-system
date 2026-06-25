"""Timeline analytics.

Summarizes activity over time across all record types: counts by calendar date,
counts by record type, the busiest day, and the overall active date range. Each
record contributes its most meaningful timestamp.
"""

from dataclasses import dataclass, field

from organizational_memory.analytics.common import count_by, iso_date
from organizational_memory.recall.timeline_search import timeline_timestamp
from organizational_memory.storage.store import MemoryStore


@dataclass(frozen=True)
class TimelineAnalytics:
    """Aggregate chronological activity analytics."""

    total: int
    activity_by_date: dict[str, int] = field(default_factory=dict)
    activity_by_type: dict[str, int] = field(default_factory=dict)
    busiest_date: str | None = None
    busiest_count: int = 0
    first_date: str | None = None
    last_date: str | None = None


def timeline_analytics(store: MemoryStore) -> TimelineAnalytics:
    """Compute :class:`TimelineAnalytics` across every stored record."""
    records = store.list_records()
    if not records:
        return TimelineAnalytics(total=0)

    activity_by_date = count_by(
        records, lambda record: iso_date(timeline_timestamp(record))
    )
    activity_by_type = count_by(records, lambda record: type(record).__name__)

    busiest_date, busiest_count = min(
        activity_by_date.items(), key=lambda item: (-item[1], item[0])
    )
    dates = sorted(activity_by_date)

    return TimelineAnalytics(
        total=len(records),
        activity_by_date=activity_by_date,
        activity_by_type=activity_by_type,
        busiest_date=busiest_date,
        busiest_count=busiest_count,
        first_date=dates[0],
        last_date=dates[-1],
    )
