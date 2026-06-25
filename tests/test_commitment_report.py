"""Tests for commitment reports."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import Commitment
from organizational_memory.models.enums import CommitmentStatus
from organizational_memory.reports.commitment_report import commitment_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   source_meeting_id="m1", status=CommitmentStatus.COMPLETED)
    )
    store.save_record(
        Commitment(id="c2", owner_id="bob", description="budget",
                   source_meeting_id="m1", status=CommitmentStatus.PENDING,
                   created_at=now - timedelta(days=10),
                   due_at=now - timedelta(days=2))
    )
    store.save_record(
        Commitment(id="c3", owner_id="alice", description="spec",
                   source_meeting_id="m2", status=CommitmentStatus.IN_PROGRESS)
    )
    return store


def test_summary(tmp_path: Path) -> None:
    report = commitment_report(_store(tmp_path), now=utc_now())
    assert report.summary["total"] == 3
    assert report.summary["open"] == 2
    assert report.summary["completed"] == 1
    assert report.summary["overdue"] == 1
    assert report.summary["missing_due_date"] == 2


def test_overdue_section(tmp_path: Path) -> None:
    report = commitment_report(_store(tmp_path), now=utc_now())
    section = report.section("Overdue commitments")
    assert section is not None
    ids = {row[0] for row in section.tables[0].rows}
    assert ids == {"c2"}


def test_by_owner(tmp_path: Path) -> None:
    report = commitment_report(_store(tmp_path), now=utc_now())
    section = report.section("By owner")
    assert section is not None
    assert section.metrics == {"alice": 2, "bob": 1}


def test_missing_due(tmp_path: Path) -> None:
    report = commitment_report(_store(tmp_path), now=utc_now())
    section = report.section("Missing due dates")
    assert section is not None
    ids = {row[0] for row in section.tables[0].rows}
    assert ids == {"c1", "c3"}


def test_empty(tmp_path: Path) -> None:
    report = commitment_report(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.summary["total"] == 0
