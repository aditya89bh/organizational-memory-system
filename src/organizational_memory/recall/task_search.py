"""Deterministic search over Task records."""

from datetime import datetime

from organizational_memory.models import Task
from organizational_memory.models.enums import Priority, TaskStatus
from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.filters import (
    rank_results,
    status_matches,
    within_window,
)
from organizational_memory.storage.store import MemoryStore


def search_tasks(
    store: MemoryStore,
    *,
    text: str | None = None,
    owner_id: str | None = None,
    priority: Priority | str | None = None,
    status: TaskStatus | str | None = None,
    due_after: datetime | None = None,
    due_before: datetime | None = None,
    source_meeting_id: str | None = None,
    min_score: float = 0.0,
) -> list[RecallResult]:
    """Return ranked Task results matching the given filters.

    ``text`` matches the task title and description; ``due_after`` /
    ``due_before`` constrain the due date to an inclusive window. The remaining
    arguments are exact-match filters.
    """
    matches: list[Task] = []
    for record in store.list_records("Task"):
        if not isinstance(record, Task):
            continue
        if owner_id is not None and record.owner_id != owner_id:
            continue
        if not status_matches(record.priority, priority):
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
