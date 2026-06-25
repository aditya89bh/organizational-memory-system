"""Deterministic search over OpenLoop records."""

from datetime import datetime

from organizational_memory.models import OpenLoop
from organizational_memory.models.enums import OpenLoopStatus
from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.filters import (
    rank_results,
    status_matches,
    within_window,
)
from organizational_memory.storage.store import MemoryStore


def search_open_loops(
    store: MemoryStore,
    *,
    text: str | None = None,
    owner_id: str | None = None,
    status: OpenLoopStatus | str | None = None,
    due_after: datetime | None = None,
    due_before: datetime | None = None,
    source_meeting_id: str | None = None,
    min_score: float = 0.0,
) -> list[RecallResult]:
    """Return ranked OpenLoop results matching the given filters.

    ``text`` matches the open loop question; ``due_after`` / ``due_before``
    constrain the due date to an inclusive window. The remaining arguments are
    exact-match filters.
    """
    matches: list[OpenLoop] = []
    for record in store.list_records("OpenLoop"):
        if not isinstance(record, OpenLoop):
            continue
        if owner_id is not None and record.owner_id != owner_id:
            continue
        if not status_matches(record.status, status):
            continue
        if not within_window(record.due_at, due_after, due_before):
            continue
        if (
            source_meeting_id is not None
            and record.source_meeting_id != source_meeting_id
        ):
            continue
        matches.append(record)
    return rank_results(matches, text, min_score)
