"""Generic typed repository over a :class:`MemoryStore`."""

from typing import Generic, TypeVar, cast

from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore

T = TypeVar("T", bound=BaseRecord)


class Repository(Generic[T]):
    """A typed view over a store scoped to a single record type."""

    def __init__(self, store: MemoryStore, record_type: type[T]) -> None:
        self._store = store
        self._record_type = record_type
        self._type_name = record_type.__name__

    @property
    def record_type(self) -> type[T]:
        """Return the model class this repository manages."""
        return self._record_type

    def add(self, record: T) -> T:
        """Persist ``record`` and return it."""
        self._store.save_record(record)
        return record

    def get(self, record_id: str) -> T | None:
        """Return the record with ``record_id`` if present."""
        record = self._store.get_record(self._type_name, record_id)
        return cast("T | None", record)

    def list(self) -> list[T]:
        """Return all records managed by this repository."""
        records = self._store.list_records(self._type_name)
        return [cast("T", record) for record in records]

    def update(self, record: T) -> T:
        """Update an existing ``record`` and return it."""
        self._store.update_record(record)
        return record

    def delete(self, record_id: str) -> bool:
        """Delete the record with ``record_id``, returning whether it existed."""
        return self._store.delete_record(self._type_name, record_id)

    def exists(self, record_id: str) -> bool:
        """Return whether a record with ``record_id`` exists."""
        return self.get(record_id) is not None
