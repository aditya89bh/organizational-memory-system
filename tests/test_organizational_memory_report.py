"""Tests for organizational memory reports."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import Commitment, Decision, OpenLoop
from organizational_memory.models.enums import CommitmentStatus, DecisionStatus
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Decision(id="d1", title="Adopt mesh", description="x", owner_id="alice",
                 status=DecisionStatus.ACCEPTED)
    )
    store.save_record(
        Decision(id="d2", title="Proposed", description="x",
                 status=DecisionStatus.PROPOSED)
    )
    store.save_record(
        OpenLoop(id="o1", question="scale?",
                 created_at=now - timedelta(days=40))
    )
    store.save_record(
        Commitment(id="c1", owner_id="bob", description="late",
                   status=CommitmentStatus.PENDING,
                   created_at=now - timedelta(days=10),
                   due_at=now - timedelta(days=2))
    )
    return store


def test_summary(tmp_path: Path) -> None:
    report = organizational_memory_report(_store(tmp_path), now=utc_now())
    assert report.summary["key_decisions"] == 1
    assert report.summary["unresolved_loops"] == 1
    assert "health_grade" in report.summary


def test_key_decisions_only_accepted(tmp_path: Path) -> None:
    report = organizational_memory_report(_store(tmp_path), now=utc_now())
    section = report.section("Key decisions")
    assert section is not None
    ids = {row[0] for row in section.tables[0].rows}
    assert ids == {"d1"}


def test_sections(tmp_path: Path) -> None:
    report = organizational_memory_report(_store(tmp_path), now=utc_now())
    titles = [s.title for s in report.sections]
    assert titles == [
        "Memory health",
        "Key decisions",
        "Unresolved loops",
        "Bottlenecks",
        "Repeated discussions",
        "Dependency risks",
        "Suggested follow-ups",
    ]


def test_follow_ups_present(tmp_path: Path) -> None:
    report = organizational_memory_report(_store(tmp_path), now=utc_now())
    section = report.section("Suggested follow-ups")
    assert section is not None
    assert any("o1" in line for line in section.body)


def test_empty(tmp_path: Path) -> None:
    report = organizational_memory_report(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.summary["key_decisions"] == 0
