"""Tests for follow-up reports."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import Commitment, OpenLoop, Task
from organizational_memory.models.enums import (
    CommitmentStatus,
    OpenLoopStatus,
    TaskStatus,
)
from organizational_memory.reports.follow_up_report import follow_up_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   status=CommitmentStatus.PENDING,
                   created_at=now - timedelta(days=10),
                   due_at=now - timedelta(days=2))
    )
    store.save_record(
        Commitment(id="c2", owner_id="bob", description="done",
                   status=CommitmentStatus.COMPLETED)
    )
    store.save_record(
        Task(id="t1", title="provision", description="x", owner_id="alice",
             status=TaskStatus.TODO)
    )
    store.save_record(
        OpenLoop(id="o1", question="scale?", status=OpenLoopStatus.OPEN)
    )
    store.save_record(
        OpenLoop(id="o2", question="resolved?", status=OpenLoopStatus.RESOLVED)
    )
    return store


def test_summary(tmp_path: Path) -> None:
    report = follow_up_report(_store(tmp_path), now=utc_now())
    assert report.summary["needs_action"] == 2
    assert report.summary["overdue"] == 1
    assert report.summary["unanswered_questions"] == 1


def test_needs_action_excludes_completed(tmp_path: Path) -> None:
    report = follow_up_report(_store(tmp_path), now=utc_now())
    section = report.section("Needs action")
    assert section is not None
    ids = {row[0] for row in section.tables[0].rows}
    assert ids == {"c1", "t1"}


def test_unanswered_questions(tmp_path: Path) -> None:
    report = follow_up_report(_store(tmp_path), now=utc_now())
    section = report.section("Unanswered questions")
    assert section is not None
    ids = {row[0] for row in section.tables[0].rows}
    assert ids == {"o1"}


def test_review_candidates(tmp_path: Path) -> None:
    report = follow_up_report(_store(tmp_path), now=utc_now())
    section = report.section("Next review candidates")
    assert section is not None
    assert any("o1" in line for line in section.body)


def test_empty(tmp_path: Path) -> None:
    report = follow_up_report(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.summary["needs_action"] == 0
