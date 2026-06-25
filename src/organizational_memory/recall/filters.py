"""Shared filtering and ranking helpers for record-specific searches.

These helpers keep the per-record-type search modules small and consistent:
they normalize status comparisons, apply date windows, and turn a filtered set
of records into ranked :class:`RecallResult` objects (keyword-ranked when a text
query is supplied, otherwise returned in a stable id order).
"""

from collections.abc import Iterable, Sequence
from datetime import datetime
from enum import Enum

from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.schemas.base import BaseRecord


def status_value(status: object) -> str:
    """Return the comparable string value of a status enum or string."""
    return status.value if isinstance(status, Enum) else str(status)


def status_matches(record_status: object, wanted: object | None) -> bool:
    """Return whether ``record_status`` equals ``wanted`` (None matches all)."""
    if wanted is None:
        return True
    return status_value(record_status) == status_value(wanted)


def within_window(
    moment: datetime | None,
    after: datetime | None,
    before: datetime | None,
) -> bool:
    """Return whether ``moment`` falls within the inclusive ``[after, before]``.

    When neither bound is set, every record passes. When a bound is set but the
    record has no timestamp, it is excluded.
    """
    if after is None and before is None:
        return True
    if moment is None:
        return False
    if after is not None and moment < after:
        return False
    return not (before is not None and moment > before)


def rank_results(
    records: Sequence[BaseRecord] | Iterable[BaseRecord],
    text: str | None,
    min_score: float = 0.0,
) -> list[RecallResult]:
    """Rank ``records`` by ``text`` if given, else return them in id order."""
    records = list(records)
    if text:
        return search_keywords(records, text, min_score=min_score)
    return [
        RecallResult(record=record, score=1.0)
        for record in sorted(records, key=lambda record: record.id)
    ]
