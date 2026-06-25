"""Deterministic search over Decision records."""

from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.filters import (
    rank_results,
    status_matches,
)
from organizational_memory.storage.store import MemoryStore


def search_decisions(
    store: MemoryStore,
    *,
    text: str | None = None,
    owner_id: str | None = None,
    status: DecisionStatus | str | None = None,
    source_meeting_id: str | None = None,
    min_score: float = 0.0,
) -> list[RecallResult]:
    """Return ranked Decision results matching the given filters.

    ``text`` is matched against the decision's title, description, rationale, and
    other text fields. The remaining arguments are exact-match filters. Results
    are keyword-ranked when ``text`` is provided, otherwise returned in id order.
    """
    matches: list[Decision] = []
    for record in store.list_records("Decision"):
        if not isinstance(record, Decision):
            continue
        if owner_id is not None and record.owner_id != owner_id:
            continue
        if not status_matches(record.status, status):
            continue
        if (
            source_meeting_id is not None
            and record.source_meeting_id != source_meeting_id
        ):
            continue
        matches.append(record)
    return rank_results(matches, text, min_score)
