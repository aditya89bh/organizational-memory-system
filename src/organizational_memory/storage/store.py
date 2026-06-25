"""Memory store interface and record (de)serialization helpers.

A :class:`MemoryStore` persists organizational memory records keyed by their
type name and identifier. Records are converted to and from JSON-compatible
dictionaries using the Phase 2 persistence helpers, so every concrete store
shares the same on-disk representation.
"""

from abc import ABC, abstractmethod
from typing import Any

from organizational_memory.exceptions import StorageError
from organizational_memory.models import (
    ActionItem,
    Commitment,
    Decision,
    Dependency,
    DiscussionTopic,
    Meeting,
    MemoryEvent,
    OpenLoop,
    Participant,
    Risk,
    Task,
)
from organizational_memory.persistence import from_dict
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.query import Query, apply_query


class RecordNotFoundError(StorageError):
    """Raised when an operation targets a record that does not exist."""

RECORD_TYPES: dict[str, type[BaseRecord]] = {
    "ActionItem": ActionItem,
    "Commitment": Commitment,
    "Decision": Decision,
    "Dependency": Dependency,
    "DiscussionTopic": DiscussionTopic,
    "Meeting": Meeting,
    "MemoryEvent": MemoryEvent,
    "OpenLoop": OpenLoop,
    "Participant": Participant,
    "Risk": Risk,
    "Task": Task,
}


def record_type_name(record: BaseRecord) -> str:
    """Return the canonical type name used to persist ``record``."""
    name = type(record).__name__
    if name not in RECORD_TYPES:
        raise KeyError(f"unknown record type: {name}")
    return name


def resolve_record_type(name: str) -> type[BaseRecord]:
    """Return the model class registered under ``name``."""
    try:
        return RECORD_TYPES[name]
    except KeyError as error:
        raise KeyError(f"unknown record type: {name}") from error


def encode_record(record: BaseRecord) -> tuple[str, str, dict[str, Any]]:
    """Return the ``(type_name, record_id, payload)`` triple for ``record``."""
    return record_type_name(record), record.id, record.to_dict()


def decode_record(type_name: str, payload: dict[str, Any]) -> BaseRecord:
    """Rebuild a record of ``type_name`` from its JSON payload."""
    return from_dict(resolve_record_type(type_name), payload)


class MemoryStore(ABC):
    """Abstract persistence interface for memory records."""

    @abstractmethod
    def save_record(self, record: BaseRecord) -> None:
        """Insert or replace ``record`` in the store."""

    @abstractmethod
    def get_record(self, record_type: str, record_id: str) -> BaseRecord | None:
        """Return the record of ``record_type`` with ``record_id`` if present."""

    @abstractmethod
    def list_records(self, record_type: str | None = None) -> list[BaseRecord]:
        """Return all records, optionally filtered by ``record_type``."""

    @abstractmethod
    def update_record(self, record: BaseRecord) -> None:
        """Replace an existing record with ``record``."""

    @abstractmethod
    def delete_record(self, record_type: str, record_id: str) -> bool:
        """Delete a record, returning whether anything was removed."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all records from the store."""

    def query(self, query: Query) -> list[BaseRecord]:
        """Return records matching ``query``, applying ordering and paging.

        The default implementation loads the candidate records (narrowed by
        ``record_type`` when set) and filters them in memory, so it behaves
        identically across every concrete store.
        """
        candidates = self.list_records(query.record_type)
        return apply_query(candidates, query)
