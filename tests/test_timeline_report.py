"""Tests for timeline reports."""

from pathlib import Path

from organizational_memory.models import Decision, Meeting, OpenLoop
from organizational_memory.reports.timeline_report import timeline_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp, utc_now


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Meeting(id="m1", title="Kickoff",
                started_at=parse_timestamp("2026-02-01T09:00:00Z"))
    )
    store.save_record(
        Decision(id="d1", title="Adopt mesh", description="x",
                 decided_at=parse_timestamp("2026-02-03T10:00:00Z"))
    )
    store.save_record(
        OpenLoop(id="o1", question="scale?",
                 created_at=parse_timestamp("2026-02-05T10:00:00Z"))
    )
    return store


def test_chronological_order(tmp_path: Path) -> None:
    report = timeline_report(_store(tmp_path), now=utc_now())
    section = report.section("Timeline")
    assert section is not None
    ids = [row[2] for row in section.tables[0].rows]
    assert ids == ["m1", "d1", "o1"]


def test_by_type(tmp_path: Path) -> None:
    report = timeline_report(_store(tmp_path), now=utc_now())
    assert report.summary["by_type"] == {"Meeting": 1, "Decision": 1, "OpenLoop": 1}


def test_window_filter(tmp_path: Path) -> None:
    report = timeline_report(
        _store(tmp_path),
        after=parse_timestamp("2026-02-02T00:00:00Z"),
        before=parse_timestamp("2026-02-04T00:00:00Z"),
        now=utc_now(),
    )
    section = report.section("Timeline")
    assert section is not None
    ids = [row[2] for row in section.tables[0].rows]
    assert ids == ["d1"]


def test_descending(tmp_path: Path) -> None:
    report = timeline_report(_store(tmp_path), ascending=False, now=utc_now())
    section = report.section("Timeline")
    assert section is not None
    ids = [row[2] for row in section.tables[0].rows]
    assert ids == ["o1", "d1", "m1"]


def test_empty(tmp_path: Path) -> None:
    report = timeline_report(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.summary["total"] == 0
