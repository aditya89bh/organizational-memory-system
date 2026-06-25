"""Tests for timeline analytics."""

from pathlib import Path

from organizational_memory.analytics.timeline_analytics import timeline_analytics
from organizational_memory.models import Commitment, Decision, OpenLoop
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Decision(
            id="d1",
            title="x",
            description="y",
            created_at=parse_timestamp("2026-01-05T10:00:00Z"),
            decided_at=parse_timestamp("2026-01-05T10:00:00Z"),
        )
    )
    store.save_record(
        Decision(
            id="d2",
            title="x",
            description="y",
            created_at=parse_timestamp("2026-01-05T12:00:00Z"),
            decided_at=parse_timestamp("2026-01-05T12:00:00Z"),
        )
    )
    store.save_record(
        Commitment(
            id="c1",
            owner_id="a",
            description="y",
            created_at=parse_timestamp("2026-01-07T09:00:00Z"),
        )
    )
    store.save_record(
        OpenLoop(
            id="o1",
            question="q?",
            created_at=parse_timestamp("2026-01-10T09:00:00Z"),
        )
    )
    return store


def test_activity_by_date(tmp_path: Path) -> None:
    report = timeline_analytics(_store(tmp_path))
    assert report.activity_by_date == {
        "2026-01-05": 2,
        "2026-01-07": 1,
        "2026-01-10": 1,
    }


def test_activity_by_type(tmp_path: Path) -> None:
    report = timeline_analytics(_store(tmp_path))
    assert report.activity_by_type == {
        "Commitment": 1,
        "Decision": 2,
        "OpenLoop": 1,
    }


def test_busiest_and_range(tmp_path: Path) -> None:
    report = timeline_analytics(_store(tmp_path))
    assert report.busiest_date == "2026-01-05"
    assert report.busiest_count == 2
    assert report.first_date == "2026-01-05"
    assert report.last_date == "2026-01-10"


def test_empty(tmp_path: Path) -> None:
    report = timeline_analytics(JSONStore(tmp_path / "e.json"))
    assert report.total == 0
    assert report.busiest_date is None
