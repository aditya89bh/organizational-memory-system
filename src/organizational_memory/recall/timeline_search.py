"""Deterministic chronological retrieval across record types.

Timeline search collects time-bearing records (meetings, decisions, commitments,
tasks, open loops, risks, and memory events), picks the most meaningful
timestamp for each, filters by an optional window, and returns them in
chronological order.
"""

from datetime import datetime

from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.filters import within_window
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import format_timestamp

TIMELINE_TYPES = (
    "Meeting",
    "Decision",
    "Commitment",
    "Task",
    "OpenLoop",
    "Risk",
    "MemoryEvent",
)

_TIMESTAMP_FIELDS = ("occurred_at", "started_at", "decided_at", "created_at")


def timeline_timestamp(record: BaseRecord) -> datetime:
    """Return the most meaningful timeline timestamp for ``record``.

    The first present value among ``occurred_at``, ``started_at``,
    ``decided_at``, and ``created_at`` is used.
    """
    for field_name in _TIMESTAMP_FIELDS:
        value = getattr(record, field_name, None)
        if isinstance(value, datetime):
            return value
    return record.created_at


def search_timeline(
    store: MemoryStore,
    *,
    after: datetime | None = None,
    before: datetime | None = None,
    ascending: bool = True,
    record_types: tuple[str, ...] | None = None,
) -> list[RecallResult]:
    """Return time-ordered results within the inclusive ``[after, before]``.

    ``record_types`` restricts which timeline types are considered; by default
    all of :data:`TIMELINE_TYPES` are included.
    """
    wanted = record_types or TIMELINE_TYPES
    entries: list[tuple[datetime, str, BaseRecord]] = []
    for type_name in wanted:
        if type_name not in TIMELINE_TYPES:
            continue
        for record in store.list_records(type_name):
            moment = timeline_timestamp(record)
            if not within_window(moment, after, before):
                continue
            entries.append((moment, record.id, record))

    entries.sort(key=lambda entry: (entry[0], entry[1]))
    if not ascending:
        entries.reverse()

    return [
        RecallResult(
            record=record,
            score=1.0,
            details={"timestamp": format_timestamp(moment)},
        )
        for moment, _, record in entries
    ]
