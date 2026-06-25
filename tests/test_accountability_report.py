"""Tests for accountability reports."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import Commitment, Task
from organizational_memory.models.enums import CommitmentStatus, TaskStatus
from organizational_memory.reports.accountability_report import accountability_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   status=CommitmentStatus.COMPLETED)
    )
    store.save_record(
        Commitment(id="c2", owner_id="alice", description="budget",
                   status=CommitmentStatus.PENDING,
                   created_at=now - timedelta(days=10),
                   due_at=now - timedelta(days=1))
    )
    store.save_record(
        Task(id="t1", title="provision", description="x", owner_id="bob",
             status=TaskStatus.TODO)
    )
    return store


def test_summary(tmp_path: Path) -> None:
    report = accountability_report(_store(tmp_path), now=utc_now())
    assert report.summary["assigned"] == 3
    assert report.summary["unassigned"] == 0
    assert report.summary["overdue"] == 1
    assert report.summary["commitments_without_due_date"] == 1
    assert report.summary["tasks_without_owner"] == 0


def test_owner_load_rows(tmp_path: Path) -> None:
    report = accountability_report(_store(tmp_path), now=utc_now())
    section = report.section("Owner load")
    assert section is not None
    owners = {row[0] for row in section.tables[0].rows}
    assert owners == {"alice", "bob"}


def test_follow_through(tmp_path: Path) -> None:
    report = accountability_report(_store(tmp_path), now=utc_now())
    section = report.section("Follow-through summary")
    assert section is not None
    rows = {row[0]: row for row in section.tables[0].rows}
    assert rows["alice"][1] == "1"  # completed


def test_empty(tmp_path: Path) -> None:
    report = accountability_report(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.summary["assigned"] == 0
