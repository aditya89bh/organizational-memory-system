"""Integration tests for reports across stores, analytics, recall, and exports."""

import json
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

import pytest

from organizational_memory.models import (
    Commitment,
    Decision,
    Meeting,
    OpenLoop,
    Task,
)
from organizational_memory.models.enums import (
    CommitmentStatus,
    DecisionStatus,
    OpenLoopStatus,
    TaskStatus,
)
from organizational_memory.recall.decision_search import search_decisions
from organizational_memory.reports.accountability_report import accountability_report
from organizational_memory.reports.exporters.csv import CSVExporter
from organizational_memory.reports.exporters.json import JSONExporter
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.reports.follow_up_report import follow_up_report
from organizational_memory.reports.meeting_summary import meeting_summary
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.reports.weekly_report import weekly_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.sqlite_store import SQLiteStore
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import parse_timestamp, utc_now

StoreFactory = Callable[[Path], MemoryStore]

NOW = utc_now()
WEEK_START = NOW - timedelta(days=7)
WEEK_END = NOW + timedelta(days=1)


def _populate(store: MemoryStore) -> None:
    store.save_record(
        Meeting(id="m1", title="Kickoff",
                started_at=NOW - timedelta(days=5),
                participants=["alice", "bob"])
    )
    store.save_record(
        Decision(id="d1", title="Adopt mesh", description="x", owner_id="alice",
                 status=DecisionStatus.ACCEPTED, source_meeting_id="m1",
                 decided_at=NOW - timedelta(days=5),
                 created_at=NOW - timedelta(days=5))
    )
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   status=CommitmentStatus.PENDING, source_meeting_id="m1",
                   created_at=NOW - timedelta(days=5),
                   due_at=NOW - timedelta(days=1))
    )
    store.save_record(
        Task(id="t1", title="provision", description="x", owner_id="bob",
             status=TaskStatus.TODO, source_meeting_id="m1",
             created_at=NOW - timedelta(days=4))
    )
    store.save_record(
        OpenLoop(id="o1", question="scale?", source_meeting_id="m1",
                 status=OpenLoopStatus.OPEN, created_at=NOW - timedelta(days=4))
    )


def _json_store(tmp_path: Path) -> MemoryStore:
    return JSONStore(tmp_path / "memory.json")


def _sqlite_store(tmp_path: Path) -> MemoryStore:
    return SQLiteStore(tmp_path / "memory.db")


_FACTORIES = [_json_store, _sqlite_store]


@pytest.mark.parametrize("factory", _FACTORIES)
def test_meeting_summary_across_stores(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    _populate(store)
    report = meeting_summary(store, "m1", now=NOW)
    assert report.summary["decisions"] == 1
    assert report.summary["commitments"] == 1
    assert report.summary["open_loops"] == 1


@pytest.mark.parametrize("factory", _FACTORIES)
def test_weekly_report_across_stores(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    _populate(store)
    report = weekly_report(store, start=WEEK_START, end=WEEK_END, now=NOW)
    assert report.summary["decisions"] == 1
    assert report.summary["overdue"] >= 1


@pytest.mark.parametrize("factory", _FACTORIES)
def test_accountability_report_across_stores(
    factory: StoreFactory, tmp_path: Path
) -> None:
    store = factory(tmp_path)
    _populate(store)
    report = accountability_report(store, now=NOW)
    assert report.summary["assigned"] == 2


def test_analytics_to_report(tmp_path: Path) -> None:
    store = _json_store(tmp_path)
    _populate(store)
    report = organizational_memory_report(store, now=NOW)
    assert "health_score" in report.summary
    assert report.summary["key_decisions"] == 1


def test_recall_to_report(tmp_path: Path) -> None:
    store = _json_store(tmp_path)
    _populate(store)
    results = search_decisions(store, status=DecisionStatus.ACCEPTED)
    assert len(results) == 1
    report = organizational_memory_report(store, now=NOW)
    section = report.section("Key decisions")
    assert section is not None
    ids = {row[0] for row in section.tables[0].rows}
    assert ids == {results[0].record.id}


def test_exporters_round_trip(tmp_path: Path) -> None:
    store = _json_store(tmp_path)
    _populate(store)
    report = follow_up_report(store, now=NOW)

    md = MarkdownExporter().export(report)
    assert md.startswith("# Follow-up report")

    loaded = json.loads(JSONExporter().export(report))
    assert loaded["title"] == "Follow-up report"

    csv_output = CSVExporter().export(report)
    assert "id,type,owner,status,due" in csv_output


def test_meeting_summary_parses_back(tmp_path: Path) -> None:
    store = _json_store(tmp_path)
    _populate(store)
    report = meeting_summary(store, "m1", now=NOW)
    text = JSONExporter().export(report)
    assert parse_timestamp(json.loads(text)["generated_at"]) == NOW
