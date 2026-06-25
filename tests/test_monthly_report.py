"""Tests for monthly reports."""

from pathlib import Path

from organizational_memory.models import (
    Commitment,
    Decision,
    DiscussionTopic,
    OpenLoop,
)
from organizational_memory.models.enums import CommitmentStatus, DecisionStatus
from organizational_memory.reports.monthly_report import monthly_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp

START = parse_timestamp("2026-02-01T00:00:00Z")
END = parse_timestamp("2026-03-01T00:00:00Z")


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Decision(id="d1", title="x", description="y",
                 status=DecisionStatus.ACCEPTED,
                 decided_at=parse_timestamp("2026-02-03T10:00:00Z"))
    )
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="y",
                   status=CommitmentStatus.COMPLETED,
                   created_at=parse_timestamp("2026-02-04T10:00:00Z"))
    )
    store.save_record(
        OpenLoop(id="o1", question="auth?",
                 created_at=parse_timestamp("2026-02-05T10:00:00Z"))
    )
    store.save_record(
        DiscussionTopic(id="dt1", title="Pricing",
                        created_at=parse_timestamp("2026-02-05T10:00:00Z"))
    )
    store.save_record(
        DiscussionTopic(id="dt2", title="pricing",
                        created_at=parse_timestamp("2026-02-12T10:00:00Z"))
    )
    return store


def test_summary(tmp_path: Path) -> None:
    report = monthly_report(_store(tmp_path), start=START, end=END)
    assert report.summary["decisions_total"] == 1
    assert report.summary["commitment_completion_rate"] == 1.0
    assert report.summary["repeated_topics"] == 1
    assert "health_grade" in report.summary


def test_sections(tmp_path: Path) -> None:
    report = monthly_report(_store(tmp_path), start=START, end=END)
    titles = [s.title for s in report.sections]
    assert titles == [
        "Decision velocity",
        "Commitment completion",
        "Open-loop trend",
        "Repeated discussions",
        "Accountability summary",
        "Memory health",
    ]


def test_open_loop_trend_window(tmp_path: Path) -> None:
    report = monthly_report(_store(tmp_path), start=START, end=END)
    section = report.section("Open-loop trend")
    assert section is not None
    assert section.tables[0].rows == [("2026-W06", "1")]


def test_repeated_discussions_section(tmp_path: Path) -> None:
    report = monthly_report(_store(tmp_path), start=START, end=END)
    section = report.section("Repeated discussions")
    assert section is not None
    assert section.metrics["topic_clusters"] == 1


def test_empty(tmp_path: Path) -> None:
    report = monthly_report(JSONStore(tmp_path / "e.json"), start=START, end=END)
    assert report.summary["decisions_total"] == 0
