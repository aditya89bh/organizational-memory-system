"""Deterministic search over Participant records."""

from organizational_memory.models import Participant
from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.filters import rank_results
from organizational_memory.storage.store import MemoryStore


def _matches(value: str | None, wanted: str | None) -> bool:
    if wanted is None:
        return True
    if value is None:
        return False
    return value.casefold() == wanted.casefold()


def search_participants(
    store: MemoryStore,
    *,
    text: str | None = None,
    name: str | None = None,
    email: str | None = None,
    role: str | None = None,
    organization: str | None = None,
    min_score: float = 0.0,
) -> list[RecallResult]:
    """Return ranked Participant results matching the given filters.

    ``text`` matches any participant text field; ``name``, ``email``, ``role``,
    and ``organization`` are case-insensitive exact-match filters.
    """
    matches: list[Participant] = []
    for record in store.list_records("Participant"):
        if not isinstance(record, Participant):
            continue
        if not _matches(record.name, name):
            continue
        if not _matches(record.email, email):
            continue
        if not _matches(record.role, role):
            continue
        if not _matches(record.organization, organization):
            continue
        matches.append(record)
    return rank_results(matches, text, min_score)
