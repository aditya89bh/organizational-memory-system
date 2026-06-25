"""Tests for decision velocity metrics."""

from datetime import datetime
from pathlib import Path

from organizational_memory.analytics.decision_velocity import decision_velocity
from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp


def _dt(value: str) -> datetime:
    return parse_timestamp(value)


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Decision(
            id="d1",
            title="Adopt Kubernetes",
            description="x",
            owner_id="alice",
            source_meeting_id="m1",
            status=DecisionStatus.ACCEPTED,
            decided_at=_dt("2026-01-05T10:00:00Z"),
        )
    )
    store.save_record(
        Decision(
            id="d2",
            title="Pricing",
            description="x",
            owner_id="alice",
            source_meeting_id="m1",
            status=DecisionStatus.PROPOSED,
            decided_at=_dt("2026-01-06T10:00:00Z"),
        )
    )
    store.save_record(
        Decision(
            id="d3",
            title="Old approach",
            description="x",
            owner_id="bob",
            source_meeting_id="m2",
            status=DecisionStatus.SUPERSEDED,
            decided_at=_dt("2026-02-02T10:00:00Z"),
        )
    )
    return store


def test_total_and_breakdowns(tmp_path: Path) -> None:
    report = decision_velocity(_store(tmp_path))
    assert report.total == 3
    assert report.by_owner == {"alice": 2, "bob": 1}
    assert report.by_meeting == {"m1": 2, "m2": 1}


def test_per_week_buckets(tmp_path: Path) -> None:
    report = decision_velocity(_store(tmp_path))
    # 2026-01-05 and 2026-01-06 are ISO week 2; 2026-02-02 is ISO week 6.
    assert report.per_week == {"2026-W02": 2, "2026-W06": 1}


def test_active_vs_superseded(tmp_path: Path) -> None:
    report = decision_velocity(_store(tmp_path))
    assert report.active == 2
    assert report.superseded == 1


def test_empty_store(tmp_path: Path) -> None:
    report = decision_velocity(JSONStore(tmp_path / "empty.json"))
    assert report.total == 0
    assert report.per_week == {}
    assert report.active == 0
