"""Integration tests for analytics across stores and the extraction pipeline."""

import json
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

from organizational_memory.analytics.decision_velocity import decision_velocity
from organizational_memory.analytics.memory_health import memory_health
from organizational_memory.analytics.reporting import (
    build_dashboard_snapshot,
    generate_report,
)
from organizational_memory.extraction.pipeline import ExtractionResult, run_extraction
from organizational_memory.models import (
    Commitment,
    Decision,
    OpenLoop,
    Risk,
    Task,
)
from organizational_memory.models.enums import (
    CommitmentStatus,
    DecisionStatus,
    OpenLoopStatus,
    RiskStatus,
    TaskStatus,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.sqlite_store import SQLiteStore
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

StoreFactory = Callable[[Path], MemoryStore]


def _populate(store: MemoryStore) -> None:
    now = utc_now()
    store.save_record(
        Decision(
            id="d1",
            title="Adopt mesh",
            description="x",
            owner_id="alice",
            status=DecisionStatus.ACCEPTED,
            decided_at=now - timedelta(days=20),
            created_at=now - timedelta(days=20),
        )
    )
    store.save_record(
        Commitment(
            id="c1",
            owner_id="alice",
            description="ship",
            status=CommitmentStatus.COMPLETED,
            created_at=now - timedelta(days=18),
        )
    )
    store.save_record(
        Task(
            id="t1",
            title="late",
            description="x",
            owner_id="bob",
            status=TaskStatus.IN_PROGRESS,
            created_at=now - timedelta(days=10),
            due_at=now - timedelta(days=2),
        )
    )
    store.save_record(
        OpenLoop(id="o1", question="scale?", status=OpenLoopStatus.OPEN)
    )
    store.save_record(
        Risk(id="r1", title="risk", description="x", status=RiskStatus.IDENTIFIED)
    )


def _json_store(tmp_path: Path) -> MemoryStore:
    return JSONStore(tmp_path / "memory.json")


def _sqlite_store(tmp_path: Path) -> MemoryStore:
    return SQLiteStore(tmp_path / "memory.db")


def test_jsonstore_backed_analytics(tmp_path: Path) -> None:
    store = _json_store(tmp_path)
    _populate(store)
    report = generate_report(store, now=utc_now())
    assert report.summary["decisions"] == 1
    assert report.summary["overdue"] == 1


def test_sqlitestore_backed_analytics(tmp_path: Path) -> None:
    store = _sqlite_store(tmp_path)
    _populate(store)
    report = generate_report(store, now=utc_now())
    assert report.summary["decisions"] == 1
    assert report.summary["overdue"] == 1


def test_stores_agree(tmp_path: Path) -> None:
    json_store = JSONStore(tmp_path / "memory.json")
    sqlite_store = SQLiteStore(tmp_path / "memory.db")
    _populate(json_store)
    _populate(sqlite_store)
    now = utc_now()
    assert decision_velocity(json_store) == decision_velocity(sqlite_store)
    assert (
        memory_health(json_store, now=now).score
        == memory_health(sqlite_store, now=now).score
    )


def _persist_result(store: MemoryStore, result: ExtractionResult) -> None:
    for group in (
        result.decisions,
        result.commitments,
        result.tasks,
        result.open_loops,
        result.dependencies,
        result.risks,
        result.action_items,
        result.topics,
    ):
        for record in group:
            store.save_record(record)


def test_extraction_to_persistence_to_analytics(tmp_path: Path) -> None:
    transcript = (
        "We decided to adopt the new billing system.\n"
        "Alice will deliver the migration plan by Friday.\n"
        "TODO: set up the staging environment.\n"
        "How do we handle existing customers?\n"
        "There is a risk that data could be lost during migration.\n"
    )
    result = run_extraction(transcript)
    store = JSONStore(tmp_path / "memory.json")
    _persist_result(store, result)

    assert len(store.list_records()) > 0
    report = generate_report(store, now=utc_now())
    assert isinstance(report.summary["decisions"], int)
    json.dumps(report.to_dict())


def test_dashboard_snapshot_generation(tmp_path: Path) -> None:
    store = _json_store(tmp_path)
    _populate(store)
    snapshot = build_dashboard_snapshot(store, now=utc_now())
    data = snapshot.to_dict()
    encoded = json.dumps(data)
    assert "dashboard" in encoded
    assert data["dashboard"]["sections"]
