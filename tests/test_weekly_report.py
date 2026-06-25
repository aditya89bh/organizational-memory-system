"""Tests for weekly reports."""

from pathlib import Path

from organizational_memory.models import Commitment, Decision, OpenLoop
from organizational_memory.models.enums import CommitmentStatus, OpenLoopStatus
from organizational_memory.reports.weekly_report import weekly_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp

START = parse_timestamp("2026-02-02T00:00:00Z")
END = parse_timestamp("2026-02-09T00:00:00Z")


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    # In window
    store.save_record(
        Decision(id="d1", title="In week", description="x",
                 decided_at=parse_timestamp("2026-02-03T10:00:00Z"),
                 created_at=parse_timestamp("2026-02-03T10:00:00Z"))
    )
    # Out of window
    store.save_record(
        Decision(id="d2", title="Later", description="x",
                 decided_at=parse_timestamp("2026-02-20T10:00:00Z"),
                 created_at=parse_timestamp("2026-02-20T10:00:00Z"))
    )
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="created in week",
                   created_at=parse_timestamp("2026-02-04T10:00:00Z"),
                   status=CommitmentStatus.PENDING)
    )
    store.save_record(
        Commitment(id="c2", owner_id="bob", description="completed in week",
                   created_at=parse_timestamp("2026-01-20T10:00:00Z"),
                   updated_at=parse_timestamp("2026-02-05T10:00:00Z"),
                   status=CommitmentStatus.COMPLETED)
    )
    store.save_record(
        OpenLoop(id="o1", question="created in week?",
                 created_at=parse_timestamp("2026-02-06T10:00:00Z"),
                 status=OpenLoopStatus.OPEN)
    )
    store.save_record(
        OpenLoop(id="o2", question="resolved in week?",
                 created_at=parse_timestamp("2026-01-15T10:00:00Z"),
                 updated_at=parse_timestamp("2026-02-07T10:00:00Z"),
                 status=OpenLoopStatus.RESOLVED)
    )
    return store


def test_window_summary(tmp_path: Path) -> None:
    report = weekly_report(_store(tmp_path), start=START, end=END)
    assert report.summary["decisions"] == 1
    assert report.summary["commitments_created"] == 1
    assert report.summary["commitments_completed"] == 1
    assert report.summary["open_loops_created"] == 1
    assert report.summary["open_loops_resolved"] == 1


def test_window_label(tmp_path: Path) -> None:
    report = weekly_report(_store(tmp_path), start=START, end=END)
    assert report.summary["window"] == (
        "2026-02-02T00:00:00Z .. 2026-02-09T00:00:00Z"
    )


def test_decisions_section_excludes_out_of_window(tmp_path: Path) -> None:
    report = weekly_report(_store(tmp_path), start=START, end=END)
    section = report.section("Decisions made")
    assert section is not None
    ids = {row[0] for row in section.tables[0].rows}
    assert ids == {"d1"}


def test_health_section_present(tmp_path: Path) -> None:
    report = weekly_report(_store(tmp_path), start=START, end=END)
    section = report.section("Memory health")
    assert section is not None
    assert "score" in section.metrics
    assert "grade" in section.metrics


def test_empty(tmp_path: Path) -> None:
    report = weekly_report(JSONStore(tmp_path / "e.json"), start=START, end=END)
    assert report.summary["decisions"] == 0
