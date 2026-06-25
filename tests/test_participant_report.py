"""Tests for participant reports."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import (
    Commitment,
    Decision,
    Meeting,
    OpenLoop,
    Participant,
    Task,
)
from organizational_memory.models.enums import CommitmentStatus
from organizational_memory.reports.participant_report import participant_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp, utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(Participant(id="alice", name="Alice Doe"))
    store.save_record(
        Meeting(id="m1", title="Kickoff",
                started_at=parse_timestamp("2026-02-01T09:00:00Z"),
                participants=["alice", "bob"])
    )
    store.save_record(
        Meeting(id="m2", title="Other",
                started_at=parse_timestamp("2026-02-02T09:00:00Z"),
                participants=["bob"])
    )
    store.save_record(Decision(id="d1", title="x", description="y", owner_id="alice"))
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   status=CommitmentStatus.PENDING,
                   created_at=now - timedelta(days=10),
                   due_at=now - timedelta(days=1))
    )
    store.save_record(Task(id="t1", title="x", description="y", owner_id="alice"))
    store.save_record(OpenLoop(id="o1", question="scale?", owner_id="alice"))
    store.save_record(Decision(id="d2", title="z", description="y", owner_id="bob"))
    return store


def test_summary(tmp_path: Path) -> None:
    report = participant_report(_store(tmp_path), "alice", now=utc_now())
    assert report.summary["meetings_attended"] == 1
    assert report.summary["decisions"] == 1
    assert report.summary["commitments"] == 1
    assert report.summary["tasks"] == 1
    assert report.summary["open_loops"] == 1
    assert report.summary["overdue"] == 1


def test_display_name_in_title(tmp_path: Path) -> None:
    report = participant_report(_store(tmp_path), "alice", now=utc_now())
    assert report.title == "Participant report: Alice Doe"


def test_unknown_participant_uses_id(tmp_path: Path) -> None:
    report = participant_report(_store(tmp_path), "carol", now=utc_now())
    assert report.title == "Participant report: carol"
    assert report.summary["meetings_attended"] == 0


def test_follow_up_load(tmp_path: Path) -> None:
    report = participant_report(_store(tmp_path), "alice", now=utc_now())
    section = report.section("Follow-up load")
    assert section is not None
    assert section.metrics["count"] == 3
