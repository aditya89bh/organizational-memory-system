"""Tests for trend analysis."""

from pathlib import Path

from organizational_memory.analytics.trends import trends
from organizational_memory.models import Commitment, Decision, OpenLoop
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp, utc_now


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Decision(
            id="d1",
            title="x",
            description="y",
            decided_at=parse_timestamp("2026-01-05T10:00:00Z"),
        )
    )
    store.save_record(
        Decision(
            id="d2",
            title="x",
            description="y",
            decided_at=parse_timestamp("2026-01-12T10:00:00Z"),
        )
    )
    store.save_record(
        Decision(
            id="d3",
            title="x",
            description="y",
            decided_at=parse_timestamp("2026-01-13T10:00:00Z"),
        )
    )
    store.save_record(
        Commitment(
            id="c1",
            owner_id="a",
            description="y",
            created_at=parse_timestamp("2026-01-05T10:00:00Z"),
        )
    )
    store.save_record(
        OpenLoop(
            id="o1",
            question="q?",
            created_at=parse_timestamp("2026-01-05T10:00:00Z"),
        )
    )
    return store


def test_weekly_decision_counts(tmp_path: Path) -> None:
    report = trends(_store(tmp_path), now=utc_now())
    buckets = {p.bucket: p.count for p in report.decisions}
    assert buckets == {"2026-W02": 1, "2026-W03": 2}


def test_change_from_previous(tmp_path: Path) -> None:
    report = trends(_store(tmp_path), now=utc_now())
    assert report.decisions[0].change == 1  # first bucket vs 0
    assert report.decisions[1].change == 1  # 2 - 1


def test_commitments_and_open_loops(tmp_path: Path) -> None:
    report = trends(_store(tmp_path), now=utc_now())
    assert report.commitments[0].count == 1
    assert report.open_loops[0].count == 1


def test_empty(tmp_path: Path) -> None:
    report = trends(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.decisions == []
    assert report.overdue == []
