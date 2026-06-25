"""Tests for organizational bottleneck metrics."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.analytics.bottlenecks import bottlenecks
from organizational_memory.models import (
    Decision,
    Dependency,
    DiscussionTopic,
    Meeting,
    OpenLoop,
    Task,
)
from organizational_memory.models.enums import OpenLoopStatus, TaskStatus
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    for index in range(2):
        store.save_record(
            Task(
                id=f"t{index}",
                title="late",
                description="x",
                owner_id="alice",
                created_at=now - timedelta(days=10),
                due_at=now - timedelta(days=3),
                status=TaskStatus.IN_PROGRESS,
            )
        )
    store.save_record(Meeting(id="m1", title="Loopy", started_at=now))
    store.save_record(OpenLoop(id="o1", question="auth?", source_meeting_id="m1"))
    store.save_record(OpenLoop(id="o2", question="billing?", source_meeting_id="m1"))
    store.save_record(
        DiscussionTopic(id="dt1", title="Recurring", source_meeting_id="m1")
    )
    store.save_record(
        DiscussionTopic(id="dt2", title="recurring", source_meeting_id="m2")
    )
    store.save_record(
        OpenLoop(
            id="o3",
            question="same q",
            status=OpenLoopStatus.OPEN,
            source_meeting_id="m1",
        )
    )
    store.save_record(
        OpenLoop(
            id="o4",
            question="same q",
            status=OpenLoopStatus.OPEN,
            source_meeting_id="m2",
        )
    )
    store.save_record(Dependency(id="x1", source_id="a", target_id="b"))
    return store


def test_overloaded_owners(tmp_path: Path) -> None:
    report = bottlenecks(_store(tmp_path), now=utc_now())
    assert report.overloaded_owners == {"alice": 2}


def test_low_signal_meetings(tmp_path: Path) -> None:
    report = bottlenecks(_store(tmp_path), now=utc_now())
    meeting_ids = {m.meeting_id for m in report.low_signal_meetings}
    assert "m1" in meeting_ids


def test_recurring_unresolved(tmp_path: Path) -> None:
    report = bottlenecks(_store(tmp_path), now=utc_now())
    keys = {cluster.key for cluster in report.recurring_unresolved}
    assert "same q" in keys


def test_blocked_records(tmp_path: Path) -> None:
    report = bottlenecks(_store(tmp_path), now=utc_now())
    assert report.blocked_records == ("a",)


def test_no_decisions_meeting_flagged(tmp_path: Path) -> None:
    # Adding a decision to m1 should remove it from low-signal meetings.
    store = _store(tmp_path)
    store.save_record(
        Decision(id="d1", title="x", description="y", source_meeting_id="m1")
    )
    report = bottlenecks(store, now=utc_now(), max_decisions=0)
    assert all(m.meeting_id != "m1" for m in report.low_signal_meetings)
