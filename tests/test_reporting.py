"""Tests for analytics report generation."""

import json
from datetime import timedelta
from pathlib import Path

from organizational_memory.analytics.reporting import (
    build_dashboard_snapshot,
    generate_report,
)
from organizational_memory.models import Commitment, Decision, OpenLoop, Risk, Task
from organizational_memory.models.enums import (
    CommitmentStatus,
    OpenLoopStatus,
    RiskStatus,
    TaskStatus,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(Decision(id="d1", title="x", description="y"))
    store.save_record(
        Commitment(
            id="c1",
            owner_id="alice",
            description="y",
            status=CommitmentStatus.COMPLETED,
        )
    )
    store.save_record(
        Task(
            id="t1",
            title="late",
            description="y",
            owner_id="alice",
            created_at=now - timedelta(days=5),
            due_at=now - timedelta(days=2),
            status=TaskStatus.IN_PROGRESS,
        )
    )
    store.save_record(OpenLoop(id="o1", question="q?", status=OpenLoopStatus.OPEN))
    store.save_record(
        Risk(
            id="r1",
            title="data loss",
            description="bad",
            status=RiskStatus.IDENTIFIED,
        )
    )
    return store


def test_summary_and_metrics(tmp_path: Path) -> None:
    report = generate_report(_store(tmp_path), now=utc_now())
    assert report.summary["decisions"] == 1
    assert report.summary["commitments"] == 1
    assert report.summary["open_loops"] == 1
    assert report.key_metrics["overdue_total"] == 1


def test_risks_include_open_risk_and_overdue(tmp_path: Path) -> None:
    report = generate_report(_store(tmp_path), now=utc_now())
    kinds = {risk["type"] for risk in report.risks}
    assert "risk" in kinds
    assert "overdue" in kinds


def test_owner_load(tmp_path: Path) -> None:
    report = generate_report(_store(tmp_path), now=utc_now())
    assert report.owner_load.get("alice", 0) >= 1


def test_report_is_json_safe(tmp_path: Path) -> None:
    report = generate_report(_store(tmp_path), now=utc_now())
    encoded = json.dumps(report.to_dict())
    assert "summary" in encoded


def test_dashboard_snapshot(tmp_path: Path) -> None:
    snapshot = build_dashboard_snapshot(_store(tmp_path), now=utc_now())
    data = snapshot.to_dict()
    assert data["dashboard"]["sections"][0]["name"] == "Summary"
    json.dumps(data)


def test_empty_store(tmp_path: Path) -> None:
    report = generate_report(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.summary["decisions"] == 0
    assert report.risks == []
