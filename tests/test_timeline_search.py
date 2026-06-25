"""Tests for timeline search."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import Decision, Meeting, MemoryEvent, Task
from organizational_memory.recall.timeline_search import (
    search_timeline,
    timeline_timestamp,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    base = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Meeting(id="m1", title="Kickoff", started_at=base, created_at=base)
    )
    store.save_record(
        Decision(
            id="d1",
            title="Adopt SQLite",
            description="x",
            created_at=base + timedelta(hours=1),
        )
    )
    store.save_record(
        Task(
            id="t1",
            title="Build it",
            description="x",
            owner_id="a",
            created_at=base + timedelta(hours=2),
        )
    )
    store.save_record(
        MemoryEvent(
            id="e1",
            event_type="created",
            entity_type="Decision",
            entity_id="d1",
            occurred_at=base + timedelta(hours=3),
            created_at=base,
        )
    )
    return store


def test_timeline_ascending(tmp_path: Path) -> None:
    results = search_timeline(_store(tmp_path))
    assert [r.record.id for r in results] == ["m1", "d1", "t1", "e1"]


def test_timeline_descending(tmp_path: Path) -> None:
    results = search_timeline(_store(tmp_path), ascending=False)
    assert [r.record.id for r in results] == ["e1", "t1", "d1", "m1"]


def test_timeline_after(tmp_path: Path) -> None:
    cutoff = utc_now() + timedelta(hours=1, minutes=30)
    results = search_timeline(_store(tmp_path), after=cutoff)
    assert [r.record.id for r in results] == ["t1", "e1"]


def test_timeline_before(tmp_path: Path) -> None:
    cutoff = utc_now() + timedelta(hours=1, minutes=30)
    results = search_timeline(_store(tmp_path), before=cutoff)
    assert [r.record.id for r in results] == ["m1", "d1"]


def test_timeline_restrict_types(tmp_path: Path) -> None:
    results = search_timeline(_store(tmp_path), record_types=("Decision", "Task"))
    assert [r.record.id for r in results] == ["d1", "t1"]


def test_timeline_timestamp_prefers_event_time() -> None:
    base = utc_now()
    event = MemoryEvent(
        event_type="x",
        entity_type="y",
        entity_id="z",
        occurred_at=base + timedelta(days=1),
        created_at=base,
    )
    assert timeline_timestamp(event) == base + timedelta(days=1)


def test_timeline_details_have_timestamp(tmp_path: Path) -> None:
    results = search_timeline(_store(tmp_path))
    assert "timestamp" in results[0].details
