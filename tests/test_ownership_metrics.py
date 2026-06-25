"""Tests for ownership metrics."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.analytics.ownership_metrics import ownership_metrics
from organizational_memory.models import Commitment, Decision, OpenLoop, Risk, Task
from organizational_memory.models.enums import (
    CommitmentStatus,
    DecisionStatus,
    TaskStatus,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Decision(
            id="d1",
            title="x",
            description="y",
            owner_id="alice",
            status=DecisionStatus.PROPOSED,
        )
    )
    store.save_record(Risk(id="r1", title="x", description="y", owner_id="alice"))
    store.save_record(
        Task(
            id="t1",
            title="x",
            description="y",
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
            description="done",
            status=CommitmentStatus.COMPLETED,
        )
    )
    store.save_record(OpenLoop(id="o1", question="unowned?"))
    return store


def test_records_by_owner(tmp_path: Path) -> None:
    report = ownership_metrics(_store(tmp_path), now=utc_now())
    assert report.records_by_owner == {"alice": 3, "bob": 1}


def test_unowned(tmp_path: Path) -> None:
    report = ownership_metrics(_store(tmp_path), now=utc_now())
    assert report.unowned == 1


def test_open_by_owner_excludes_completed(tmp_path: Path) -> None:
    report = ownership_metrics(_store(tmp_path), now=utc_now())
    # bob's only record is completed, so excluded from open work.
    assert "bob" not in report.open_by_owner
    assert report.open_by_owner.get("alice", 0) >= 1


def test_overdue_by_owner(tmp_path: Path) -> None:
    report = ownership_metrics(_store(tmp_path), now=utc_now())
    assert report.overdue_by_owner == {"alice": 1}


def test_decisions_and_risks(tmp_path: Path) -> None:
    report = ownership_metrics(_store(tmp_path), now=utc_now())
    assert report.decisions_by_owner == {"alice": 1}
    assert report.risks_by_owner == {"alice": 1}


def test_empty(tmp_path: Path) -> None:
    report = ownership_metrics(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.records_by_owner == {}
    assert report.unowned == 0
