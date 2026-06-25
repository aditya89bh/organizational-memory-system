"""Tests for overdue work metrics."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.analytics.overdue_tasks import overdue_tasks
from organizational_memory.models import Commitment, OpenLoop, Task
from organizational_memory.models.enums import (
    CommitmentStatus,
    OpenLoopStatus,
    TaskStatus,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Task(
            id="t1",
            title="late task",
            description="x",
            owner_id="alice",
            source_meeting_id="m1",
            created_at=now - timedelta(days=10),
            due_at=now - timedelta(days=5),
            status=TaskStatus.IN_PROGRESS,
        )
    )
    store.save_record(
        Task(
            id="t2",
            title="done late",
            description="x",
            owner_id="alice",
            created_at=now - timedelta(days=10),
            due_at=now - timedelta(days=3),
            status=TaskStatus.DONE,
        )
    )
    store.save_record(
        Task(
            id="t3",
            title="future",
            description="x",
            owner_id="bob",
            due_at=now + timedelta(days=3),
        )
    )
    store.save_record(
        Commitment(
            id="c1",
            owner_id="bob",
            description="late commit",
            source_meeting_id="m2",
            created_at=now - timedelta(days=10),
            due_at=now - timedelta(days=1),
            status=CommitmentStatus.PENDING,
        )
    )
    store.save_record(
        OpenLoop(
            id="o1",
            question="late loop?",
            owner_id="alice",
            created_at=now - timedelta(days=10),
            due_at=now - timedelta(days=8),
            status=OpenLoopStatus.OPEN,
        )
    )
    return store


def test_overdue_counts(tmp_path: Path) -> None:
    report = overdue_tasks(_store(tmp_path), now=utc_now())
    assert report.total == 3
    assert report.tasks == 1
    assert report.commitments == 1
    assert report.open_loops == 1


def test_done_and_future_excluded(tmp_path: Path) -> None:
    report = overdue_tasks(_store(tmp_path), now=utc_now())
    ids = {item.id for item in report.items}
    assert "t2" not in ids
    assert "t3" not in ids


def test_sorted_by_days_overdue(tmp_path: Path) -> None:
    report = overdue_tasks(_store(tmp_path), now=utc_now())
    assert [item.id for item in report.items] == ["o1", "t1", "c1"]
    assert report.items[0].days_overdue >= report.items[1].days_overdue


def test_breakdowns(tmp_path: Path) -> None:
    report = overdue_tasks(_store(tmp_path), now=utc_now())
    assert report.by_owner == {"alice": 2, "bob": 1}
    assert report.by_meeting == {"m1": 1, "m2": 1, "none": 1}


def test_empty(tmp_path: Path) -> None:
    report = overdue_tasks(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.total == 0
    assert report.items == []
