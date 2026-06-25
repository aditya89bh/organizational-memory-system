"""Tests for task search."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import Task
from organizational_memory.models.enums import Priority, TaskStatus
from organizational_memory.recall.task_search import search_tasks
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Task(
            id="t1",
            title="Launch landing page",
            description="ship the marketing site",
            owner_id="alice",
            priority=Priority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            due_at=now + timedelta(days=3),
            source_meeting_id="m1",
        )
    )
    store.save_record(
        Task(
            id="t2",
            title="Refactor billing",
            description="clean up billing module",
            owner_id="bob",
            priority=Priority.LOW,
            status=TaskStatus.TODO,
            due_at=now + timedelta(days=40),
            source_meeting_id="m2",
        )
    )
    return store


def test_search_by_text(tmp_path: Path) -> None:
    results = search_tasks(_store(tmp_path), text="billing")
    assert [r.record.id for r in results] == ["t2"]


def test_search_by_owner(tmp_path: Path) -> None:
    assert [r.record.id for r in search_tasks(_store(tmp_path), owner_id="alice")] == [
        "t1"
    ]


def test_search_by_priority(tmp_path: Path) -> None:
    results = search_tasks(_store(tmp_path), priority=Priority.HIGH)
    assert [r.record.id for r in results] == ["t1"]


def test_search_by_status(tmp_path: Path) -> None:
    results = search_tasks(_store(tmp_path), status="todo")
    assert [r.record.id for r in results] == ["t2"]


def test_search_by_due_window(tmp_path: Path) -> None:
    now = utc_now()
    results = search_tasks(_store(tmp_path), due_before=now + timedelta(days=7))
    assert [r.record.id for r in results] == ["t1"]


def test_search_by_meeting(tmp_path: Path) -> None:
    results = search_tasks(_store(tmp_path), source_meeting_id="m2")
    assert [r.record.id for r in results] == ["t2"]


def test_no_filters_returns_all(tmp_path: Path) -> None:
    assert [r.record.id for r in search_tasks(_store(tmp_path))] == ["t1", "t2"]
