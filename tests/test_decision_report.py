"""Tests for decision reports."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.reports.decision_report import decision_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Decision(id="d1", title="Adopt mesh", description="x", owner_id="alice",
                 source_meeting_id="m1", status=DecisionStatus.ACCEPTED,
                 rationale="It   scales\nbetter than the alternative.")
    )
    store.save_record(
        Decision(id="d2", title="Old proposal", description="x", owner_id="bob",
                 source_meeting_id="m1", status=DecisionStatus.PROPOSED,
                 created_at=now - timedelta(days=90))
    )
    store.save_record(
        Decision(id="d3", title="Fresh proposal", description="x", owner_id="alice",
                 source_meeting_id="m2", status=DecisionStatus.PROPOSED,
                 created_at=now - timedelta(days=1))
    )
    return store


def test_summary(tmp_path: Path) -> None:
    report = decision_report(_store(tmp_path), now=utc_now())
    assert report.summary["total"] == 3
    assert report.summary["accepted"] == 1
    assert report.summary["proposed"] == 2
    assert report.summary["stale"] == 1


def test_by_owner_section(tmp_path: Path) -> None:
    report = decision_report(_store(tmp_path), now=utc_now())
    section = report.section("By owner")
    assert section is not None
    assert section.metrics == {"alice": 2, "bob": 1}


def test_rationale_excerpt_collapsed(tmp_path: Path) -> None:
    report = decision_report(_store(tmp_path), now=utc_now())
    section = report.section("Rationale excerpts")
    assert section is not None
    rows = section.tables[0].rows
    assert rows == [("d1", "Adopt mesh", "It scales better than the alternative.")]


def test_stale_only_old_proposed(tmp_path: Path) -> None:
    report = decision_report(_store(tmp_path), now=utc_now())
    section = report.section("Stale decisions")
    assert section is not None
    ids = {row[0] for row in section.tables[0].rows}
    assert ids == {"d2"}


def test_empty(tmp_path: Path) -> None:
    report = decision_report(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.summary["total"] == 0
