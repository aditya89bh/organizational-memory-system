"""Tests that load the deterministic analytics benchmark fixtures."""

import json
from pathlib import Path
from typing import Any

from organizational_memory.analytics.commitment_completion import (
    commitment_completion,
)
from organizational_memory.analytics.decision_velocity import decision_velocity
from organizational_memory.analytics.memory_health import memory_health
from organizational_memory.analytics.open_loop_metrics import open_loop_metrics
from organizational_memory.analytics.overdue_tasks import overdue_tasks
from organizational_memory.analytics.reporting import generate_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp

FIXTURES = Path(__file__).resolve().parents[1] / "examples" / "analytics"


def _expected() -> dict[str, Any]:
    text = (FIXTURES / "analytics_expected_metrics.json").read_text(encoding="utf-8")
    data: dict[str, Any] = json.loads(text)
    return data


def _store() -> JSONStore:
    return JSONStore(FIXTURES / "analytics_memory_snapshot.json")


def test_fixture_files_exist() -> None:
    assert (FIXTURES / "analytics_memory_snapshot.json").exists()
    assert (FIXTURES / "analytics_meetings.json").exists()
    assert (FIXTURES / "analytics_expected_metrics.json").exists()


def test_snapshot_loads() -> None:
    records = _store().list_records()
    assert len(records) > 0


def test_decision_velocity_matches_expected() -> None:
    expected = _expected()["decision_velocity"]
    report = decision_velocity(_store())
    assert report.total == expected["total"]
    assert report.active == expected["active"]
    assert report.superseded == expected["superseded"]
    assert report.per_week == expected["per_week"]
    assert report.by_owner == expected["by_owner"]


def test_commitment_completion_matches_expected() -> None:
    expected = _expected()["commitment_completion"]
    report = commitment_completion(_store())
    assert report.total == expected["total"]
    assert report.completed == expected["completed"]
    assert report.open == expected["open"]
    assert report.completion_rate == expected["completion_rate"]


def test_overdue_matches_expected() -> None:
    now = parse_timestamp(_expected()["now"])
    expected = _expected()["overdue"]
    report = overdue_tasks(_store(), now=now)
    assert report.total == expected["total"]
    assert report.tasks == expected["tasks"]
    assert report.commitments == expected["commitments"]
    assert report.open_loops == expected["open_loops"]


def test_open_loops_match_expected() -> None:
    now = parse_timestamp(_expected()["now"])
    expected = _expected()["open_loops"]
    report = open_loop_metrics(_store(), now=now)
    assert report.total == expected["total"]
    assert report.unresolved == expected["unresolved"]
    assert report.resolved == expected["resolved"]


def test_memory_health_matches_expected() -> None:
    now = parse_timestamp(_expected()["now"])
    expected = _expected()["memory_health"]
    report = memory_health(_store(), now=now)
    assert report.score == expected["score"]
    assert report.grade == expected["grade"]


def test_report_summary_matches_expected() -> None:
    now = parse_timestamp(_expected()["now"])
    expected = _expected()["report_summary"]
    report = generate_report(_store(), now=now)
    assert report.summary == expected
