"""Tests for the memory store interface and serialization helpers."""

import pytest

from organizational_memory.models import Decision, Meeting
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import (
    RECORD_TYPES,
    MemoryStore,
    decode_record,
    encode_record,
    record_type_name,
    resolve_record_type,
)


class FakeStore(MemoryStore):
    """A minimal in-memory store used to exercise the interface."""

    def __init__(self) -> None:
        self._data: dict[tuple[str, str], BaseRecord] = {}

    def save_record(self, record: BaseRecord) -> None:
        self._data[(record_type_name(record), record.id)] = record

    def get_record(self, record_type: str, record_id: str) -> BaseRecord | None:
        return self._data.get((record_type, record_id))

    def list_records(self, record_type: str | None = None) -> list[BaseRecord]:
        records = list(self._data.values())
        if record_type is not None:
            records = [r for r in records if record_type_name(r) == record_type]
        return sorted(records, key=lambda r: r.id)

    def update_record(self, record: BaseRecord) -> None:
        self._data[(record_type_name(record), record.id)] = record

    def delete_record(self, record_type: str, record_id: str) -> bool:
        return self._data.pop((record_type, record_id), None) is not None

    def clear(self) -> None:
        self._data.clear()


def test_record_type_name() -> None:
    assert record_type_name(Decision(title="t", description="d")) == "Decision"


def test_record_type_name_unknown() -> None:
    class Other(BaseRecord):
        pass

    with pytest.raises(KeyError):
        record_type_name(Other())


def test_resolve_record_type() -> None:
    assert resolve_record_type("Meeting") is Meeting


def test_resolve_record_type_unknown() -> None:
    with pytest.raises(KeyError):
        resolve_record_type("Nope")


def test_encode_decode_roundtrip() -> None:
    decision = Decision(title="Ship", description="Ship on Friday")
    type_name, record_id, payload = encode_record(decision)
    assert type_name == "Decision"
    assert record_id == decision.id
    restored = decode_record(type_name, payload)
    assert isinstance(restored, Decision)
    assert restored.id == decision.id
    assert restored.title == "Ship"


def test_registry_covers_expected_types() -> None:
    assert {"Meeting", "Decision", "Commitment", "Task", "OpenLoop"} <= set(
        RECORD_TYPES
    )


def test_fake_store_crud() -> None:
    store = FakeStore()
    decision = Decision(title="t", description="d")
    store.save_record(decision)
    assert store.get_record("Decision", decision.id) is decision
    assert store.list_records("Decision") == [decision]
    assert store.delete_record("Decision", decision.id) is True
    assert store.get_record("Decision", decision.id) is None
    store.save_record(decision)
    store.clear()
    assert store.list_records() == []
