"""Tests for open loop metrics."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.analytics.open_loop_metrics import open_loop_metrics
from organizational_memory.models import OpenLoop
from organizational_memory.models.enums import OpenLoopStatus
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        OpenLoop(
            id="o1",
            question="auth?",
            owner_id="alice",
            status=OpenLoopStatus.OPEN,
            source_meeting_id="m1",
            created_at=now - timedelta(days=10),
        )
    )
    store.save_record(
        OpenLoop(
            id="o2",
            question="billing?",
            owner_id="bob",
            status=OpenLoopStatus.OPEN,
            source_meeting_id="m1",
            created_at=now - timedelta(days=2),
        )
    )
    store.save_record(
        OpenLoop(
            id="o3",
            question="done?",
            owner_id="alice",
            status=OpenLoopStatus.RESOLVED,
            source_meeting_id="m2",
            created_at=now - timedelta(days=30),
        )
    )
    return store


def test_counts(tmp_path: Path) -> None:
    report = open_loop_metrics(_store(tmp_path), now=utc_now())
    assert report.total == 3
    assert report.unresolved == 2
    assert report.resolved == 1


def test_average_age(tmp_path: Path) -> None:
    report = open_loop_metrics(_store(tmp_path), now=utc_now())
    # unresolved ages ~10 and ~2 days -> average ~6
    assert 5.5 <= report.average_age_days <= 6.5


def test_oldest_unresolved_order(tmp_path: Path) -> None:
    report = open_loop_metrics(_store(tmp_path), now=utc_now())
    assert [age.id for age in report.oldest_unresolved] == ["o1", "o2"]
    assert report.oldest_unresolved[0].age_days > report.oldest_unresolved[1].age_days


def test_breakdowns(tmp_path: Path) -> None:
    report = open_loop_metrics(_store(tmp_path), now=utc_now())
    assert report.by_owner == {"alice": 2, "bob": 1}
    assert report.by_meeting == {"m1": 2, "m2": 1}


def test_empty(tmp_path: Path) -> None:
    report = open_loop_metrics(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.total == 0
    assert report.average_age_days == 0.0
    assert report.oldest_unresolved == []
