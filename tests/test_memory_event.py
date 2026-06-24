"""Tests for the MemoryEvent model."""

from datetime import UTC, datetime

from organizational_memory.models import MemoryEvent


def test_memory_event_defaults() -> None:
    event = MemoryEvent(
        event_type="decision.created",
        entity_type="decision",
        entity_id="d1",
    )
    assert event.actor_id is None
    assert event.payload == {}
    assert event.occurred_at.tzinfo is not None


def test_memory_event_full_construction() -> None:
    event = MemoryEvent(
        event_type="task.updated",
        entity_type="task",
        entity_id="t1",
        occurred_at=datetime(2026, 6, 24, 9, 0, tzinfo=UTC),
        actor_id="alice",
        payload={"status": "done", "version": 2},
        metadata={"trace": "abc"},
    )
    assert event.payload["version"] == 2
    assert event.actor_id == "alice"


def test_memory_event_serialization() -> None:
    event = MemoryEvent(
        event_type="task.updated",
        entity_type="task",
        entity_id="t1",
        occurred_at=datetime(2026, 6, 24, 9, 0, tzinfo=UTC),
    )
    data = event.to_dict()
    assert data["event_type"] == "task.updated"
    assert data["occurred_at"] == "2026-06-24T09:00:00Z"
