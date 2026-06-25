"""Typed, deterministic query API for memory records."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from organizational_memory.schemas.base import BaseRecord

_TEXT_FIELDS = (
    "title",
    "description",
    "question",
    "summary",
    "name",
    "event_type",
)


@dataclass(frozen=True)
class Query:
    """A declarative filter over memory records.

    All criteria are combined with logical AND. Unset (``None``) criteria are
    ignored. ``created_after`` and ``created_before`` are inclusive bounds.
    """

    record_type: str | None = None
    owner_id: str | None = None
    status: str | None = None
    source_meeting_id: str | None = None
    text_contains: str | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    limit: int | None = None
    offset: int = 0


def _status_value(status: object) -> str:
    return status.value if isinstance(status, Enum) else str(status)


def _text_blob(record: BaseRecord) -> str:
    parts: list[str] = []
    for field_name in _TEXT_FIELDS:
        value = getattr(record, field_name, None)
        if isinstance(value, str):
            parts.append(value)
    return " ".join(parts).lower()


def matches(record: BaseRecord, query: Query) -> bool:
    """Return whether ``record`` satisfies every set criterion in ``query``."""
    owner = getattr(record, "owner_id", None)
    status = getattr(record, "status", None)
    meeting = getattr(record, "source_meeting_id", None)

    if query.record_type is not None and type(record).__name__ != query.record_type:
        return False
    if query.owner_id is not None and owner != query.owner_id:
        return False
    if query.status is not None and (
        status is None or _status_value(status) != query.status
    ):
        return False
    if query.source_meeting_id is not None and meeting != query.source_meeting_id:
        return False
    if query.text_contains is not None and (
        query.text_contains.lower() not in _text_blob(record)
    ):
        return False
    if query.created_after is not None and record.created_at < query.created_after:
        return False
    return not (
        query.created_before is not None and record.created_at > query.created_before
    )


def apply_query(records: Iterable[BaseRecord], query: Query) -> list[BaseRecord]:
    """Filter, order, and paginate ``records`` according to ``query``."""
    selected = [record for record in records if matches(record, query)]
    selected.sort(key=lambda record: (record.created_at, record.id))
    start = max(query.offset, 0)
    if query.limit is None:
        return selected[start:]
    return selected[start : start + query.limit]
