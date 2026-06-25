"""Tests for the memory event repository."""

from pathlib import Path

from organizational_memory.models import MemoryEvent
from organizational_memory.storage.event_repository import EventRepository
from organizational_memory.storage.json_store import JSONStore


def _repo(tmp_path: Path) -> EventRepository:
    return EventRepository(JSONStore(tmp_path / "memory.json"))


def _event() -> MemoryEvent:
    return MemoryEvent(
        event_type="decision.created",
        entity_type="decision",
        entity_id="d1",
    )


def test_add_get(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    event = repo.add(_event())
    fetched = repo.get(event.id)
    assert fetched is not None
    assert fetched.event_type == "decision.created"
    assert fetched.entity_id == "d1"


def test_list(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    repo.add(_event())
    repo.add(_event())
    assert len(repo.list()) == 2


def test_update(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    event = repo.add(_event())
    event.actor_id = "alice"
    repo.update(event)
    fetched = repo.get(event.id)
    assert fetched is not None
    assert fetched.actor_id == "alice"


def test_delete(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    event = repo.add(_event())
    assert repo.delete(event.id) is True
    assert repo.get(event.id) is None


def test_preserves_occurred_at(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    event = repo.add(_event())
    fetched = repo.get(event.id)
    assert fetched is not None
    assert fetched.occurred_at == event.occurred_at
