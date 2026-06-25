"""Tests for productivity metrics."""

from pathlib import Path

from organizational_memory.analytics.productivity import productivity
from organizational_memory.models import (
    Commitment,
    Decision,
    Meeting,
    OpenLoop,
    Task,
)
from organizational_memory.models.enums import (
    CommitmentStatus,
    OpenLoopStatus,
    TaskStatus,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp, utc_now


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(Meeting(id="m1", title="Sync", started_at=utc_now()))
    store.save_record(Decision(id="d1", title="x", description="y"))
    store.save_record(
        Task(id="t1", title="x", description="y", owner_id="a", status=TaskStatus.DONE)
    )
    store.save_record(
        Task(
            id="t2",
            title="x",
            description="y",
            owner_id="a",
            status=TaskStatus.IN_PROGRESS,
        )
    )
    store.save_record(
        Commitment(
            id="c1",
            owner_id="a",
            description="y",
            status=CommitmentStatus.COMPLETED,
            created_at=parse_timestamp("2026-01-05T10:00:00Z"),
        )
    )
    store.save_record(
        OpenLoop(id="o1", question="q?", status=OpenLoopStatus.OPEN)
    )
    return store


def test_work_ratios(tmp_path: Path) -> None:
    report = productivity(_store(tmp_path))
    # work items: t1(done), t2(open), c1(completed), o1(open) -> 4
    assert report.total_work == 4
    assert report.closed_work == 2
    assert report.open_work == 2
    assert report.closed_work_ratio == 0.5
    assert report.unresolved_work_ratio == 0.5


def test_structured_outputs_per_meeting(tmp_path: Path) -> None:
    report = productivity(_store(tmp_path))
    # structured: d1, t1, t2, c1, o1 = 5; meetings = 1 -> 5.0
    assert report.structured_outputs_per_meeting == 5.0


def test_completed_commitments_per_week(tmp_path: Path) -> None:
    report = productivity(_store(tmp_path))
    assert report.completed_commitments_per_week == {"2026-W02": 1}


def test_empty(tmp_path: Path) -> None:
    report = productivity(JSONStore(tmp_path / "e.json"))
    assert report.total_work == 0
    assert report.closed_work_ratio == 0.0
    assert report.structured_outputs_per_meeting == 0.0
