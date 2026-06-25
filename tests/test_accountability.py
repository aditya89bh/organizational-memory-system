"""Tests for accountability metrics."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.analytics.accountability import accountability
from organizational_memory.models import ActionItem, Commitment, OpenLoop, Task
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
            title="done task",
            description="x",
            owner_id="alice",
            status=TaskStatus.DONE,
        )
    )
    store.save_record(
        Task(
            id="t2",
            title="late task",
            description="x",
            owner_id="alice",
            status=TaskStatus.IN_PROGRESS,
            created_at=now - timedelta(days=5),
            due_at=now - timedelta(days=1),
        )
    )
    store.save_record(
        Commitment(
            id="c1",
            owner_id="bob",
            description="no due date",
            status=CommitmentStatus.PENDING,
        )
    )
    store.save_record(OpenLoop(id="o1", question="unowned loop?"))
    store.save_record(
        ActionItem(id="a1", description="unassigned action", status="open")
    )
    store.save_record(
        OpenLoop(
            id="o2",
            question="bob loop",
            owner_id="bob",
            status=OpenLoopStatus.OPEN,
        )
    )
    return store


def test_assigned_vs_unassigned(tmp_path: Path) -> None:
    report = accountability(_store(tmp_path), now=utc_now())
    # owned: t1,t2 (alice), c1,o2 (bob) = 4; unassigned: o1, a1 = 2
    assert report.assigned == 4
    assert report.unassigned == 2


def test_follow_through_score(tmp_path: Path) -> None:
    report = accountability(_store(tmp_path), now=utc_now())
    alice = next(o for o in report.owners if o.owner == "alice")
    # completed=1 (t1), open=1 (t2) -> 1/2
    assert alice.completed == 1
    assert alice.open == 1
    assert alice.overdue == 1
    assert alice.follow_through_score == 0.5


def test_unresolved_by_owner(tmp_path: Path) -> None:
    report = accountability(_store(tmp_path), now=utc_now())
    assert report.unresolved_by_owner.get("alice") == 1
    assert report.unresolved_by_owner.get("bob") == 2


def test_commitments_without_due_date(tmp_path: Path) -> None:
    report = accountability(_store(tmp_path), now=utc_now())
    assert report.commitments_without_due_date == 1


def test_empty(tmp_path: Path) -> None:
    report = accountability(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.assigned == 0
    assert report.owners == []
