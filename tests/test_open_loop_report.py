"""Tests for open loop reports."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import OpenLoop
from organizational_memory.models.enums import OpenLoopStatus
from organizational_memory.reports.open_loop_report import open_loop_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        OpenLoop(id="o1", question="scale?", owner_id="alice",
                 source_meeting_id="m1", status=OpenLoopStatus.OPEN,
                 created_at=now - timedelta(days=10))
    )
    store.save_record(
        OpenLoop(id="o2", question="budget?", owner_id="bob",
                 source_meeting_id="m1", status=OpenLoopStatus.OPEN,
                 created_at=now - timedelta(days=2),
                 due_at=now - timedelta(days=1))
    )
    store.save_record(
        OpenLoop(id="o3", question="vendor?", source_meeting_id="m2",
                 status=OpenLoopStatus.RESOLVED)
    )
    return store


def test_summary(tmp_path: Path) -> None:
    report = open_loop_report(_store(tmp_path), now=utc_now())
    assert report.summary["total"] == 3
    assert report.summary["unresolved"] == 2
    assert report.summary["resolved"] == 1
    assert report.summary["overdue"] == 1


def test_oldest_unresolved_order(tmp_path: Path) -> None:
    report = open_loop_report(_store(tmp_path), now=utc_now())
    section = report.section("Oldest unresolved")
    assert section is not None
    ids = [row[0] for row in section.tables[0].rows]
    assert ids[0] == "o1"


def test_overdue_section(tmp_path: Path) -> None:
    report = open_loop_report(_store(tmp_path), now=utc_now())
    section = report.section("Overdue")
    assert section is not None
    ids = {row[0] for row in section.tables[0].rows}
    assert ids == {"o2"}


def test_by_owner(tmp_path: Path) -> None:
    report = open_loop_report(_store(tmp_path), now=utc_now())
    section = report.section("By owner")
    assert section is not None
    assert section.metrics == {"alice": 1, "bob": 1, "unassigned": 1}


def test_empty(tmp_path: Path) -> None:
    report = open_loop_report(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.summary["total"] == 0
