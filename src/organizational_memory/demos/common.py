"""Shared, deterministic building blocks for the bundled demos.

Demos run the real pipeline (extraction, persistence, recall, analytics,
reports) but stabilize record identifiers and timestamps so their printed
output is fully deterministic and reproducible. Everything runs in memory with
no disk, network, or external dependencies.
"""

from collections.abc import Sequence
from datetime import UTC, datetime

from organizational_memory.extraction.pipeline import ExtractionResult, run_extraction
from organizational_memory.models import Meeting
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import (
    MemoryStore,
    RecordNotFoundError,
    record_type_name,
)

REFERENCE_NOW = datetime(2026, 3, 2, 9, 0, tzinfo=UTC)
"""Fixed reference time used for all deterministic analytics and reports."""

BASE_TIME = datetime(2026, 2, 24, 9, 0, tzinfo=UTC)
"""Fixed creation time stamped onto every demo record."""

_GROUPS: tuple[tuple[str, str], ...] = (
    ("participants", "participant"),
    ("decisions", "decision"),
    ("commitments", "commitment"),
    ("tasks", "task"),
    ("open_loops", "openloop"),
    ("dependencies", "dependency"),
    ("risks", "risk"),
    ("action_items", "actionitem"),
    ("topics", "topic"),
)


class InMemoryStore(MemoryStore):
    """A hermetic, in-memory :class:`MemoryStore` used by the demos."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, BaseRecord]] = {}

    def save_record(self, record: BaseRecord) -> None:
        name = record_type_name(record)
        self._data.setdefault(name, {})[record.id] = record

    def get_record(self, record_type: str, record_id: str) -> BaseRecord | None:
        return self._data.get(record_type, {}).get(record_id)

    def list_records(self, record_type: str | None = None) -> list[BaseRecord]:
        names = [record_type] if record_type is not None else sorted(self._data)
        records: list[BaseRecord] = []
        for name in names:
            for record_id in sorted(self._data.get(name, {})):
                records.append(self._data[name][record_id])
        return records

    def update_record(self, record: BaseRecord) -> None:
        name = record_type_name(record)
        if record.id not in self._data.get(name, {}):
            raise RecordNotFoundError(f"{name} {record.id} does not exist")
        self._data[name][record.id] = record

    def delete_record(self, record_type: str, record_id: str) -> bool:
        bucket = self._data.get(record_type, {})
        if record_id not in bucket:
            return False
        del bucket[record_id]
        if not bucket:
            self._data.pop(record_type, None)
        return True

    def clear(self) -> None:
        self._data = {}


def _stabilize(
    records: Sequence[BaseRecord],
    prefix: str,
    when: datetime,
    meeting_id: str,
) -> None:
    for index, record in enumerate(records, start=1):
        record.id = f"{prefix}-{index}"
        record.created_at = when
        record.updated_at = when
        if hasattr(record, "source_meeting_id"):
            record.source_meeting_id = meeting_id


def ingest_meeting(
    store: InMemoryStore,
    text: str,
    *,
    meeting_id: str,
    title: str,
    when: datetime = BASE_TIME,
) -> ExtractionResult:
    """Extract ``text``, stabilize records, and persist them under ``meeting_id``."""
    result = run_extraction(text)
    store.save_record(
        Meeting(
            id=meeting_id,
            title=title,
            started_at=when,
            created_at=when,
            updated_at=when,
            participants=[participant.name for participant in result.participants],
            source="demo",
        )
    )
    for attr, suffix in _GROUPS:
        records: list[BaseRecord] = getattr(result, attr)
        _stabilize(records, f"{meeting_id}-{suffix}", when, meeting_id)
        for record in records:
            store.save_record(record)
    return result


def heading(title: str) -> list[str]:
    """Return a deterministic section heading block."""
    return ["", title, "=" * len(title)]
