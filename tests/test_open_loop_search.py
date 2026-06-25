"""Tests for open loop search."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import OpenLoop
from organizational_memory.models.enums import OpenLoopStatus
from organizational_memory.recall.open_loop_search import search_open_loops
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        OpenLoop(
            id="o1",
            question="How do we handle auth?",
            owner_id="alice",
            status=OpenLoopStatus.OPEN,
            due_at=now + timedelta(days=2),
            source_meeting_id="m1",
        )
    )
    store.save_record(
        OpenLoop(
            id="o2",
            question="What about billing retries?",
            owner_id="bob",
            status=OpenLoopStatus.RESOLVED,
            due_at=now + timedelta(days=20),
            source_meeting_id="m2",
        )
    )
    return store


def test_search_by_text(tmp_path: Path) -> None:
    results = search_open_loops(_store(tmp_path), text="auth")
    assert [r.record.id for r in results] == ["o1"]


def test_search_by_owner(tmp_path: Path) -> None:
    results = search_open_loops(_store(tmp_path), owner_id="bob")
    assert [r.record.id for r in results] == ["o2"]


def test_search_by_status(tmp_path: Path) -> None:
    results = search_open_loops(_store(tmp_path), status="open")
    assert [r.record.id for r in results] == ["o1"]


def test_search_by_due_window(tmp_path: Path) -> None:
    cutoff = utc_now() + timedelta(days=5)
    results = search_open_loops(_store(tmp_path), due_before=cutoff)
    assert [r.record.id for r in results] == ["o1"]


def test_search_by_meeting(tmp_path: Path) -> None:
    results = search_open_loops(_store(tmp_path), source_meeting_id="m2")
    assert [r.record.id for r in results] == ["o2"]


def test_no_filters_returns_all(tmp_path: Path) -> None:
    assert [r.record.id for r in search_open_loops(_store(tmp_path))] == ["o1", "o2"]
