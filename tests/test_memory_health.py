"""Tests for the memory health score."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.analytics.memory_health import memory_health
from organizational_memory.models import Commitment, Decision, OpenLoop, Task
from organizational_memory.models.enums import (
    CommitmentStatus,
    DecisionStatus,
    OpenLoopStatus,
    TaskStatus,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def test_empty_store_is_healthy(tmp_path: Path) -> None:
    report = memory_health(JSONStore(tmp_path / "e.json"), now=utc_now())
    assert report.score == 100.0
    assert report.grade == "A"
    assert report.recommendations == []


def test_components_present(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Decision(id="d1", title="x", description="y", metadata={"k": "v"})
    )
    report = memory_health(store, now=utc_now())
    names = {c.name for c in report.components}
    assert names == {
        "open_loop_resolution",
        "overdue_work",
        "ownership_coverage",
        "decision_freshness",
        "discussion_focus",
        "metadata_completeness",
    }
    assert abs(sum(c.weight for c in report.components) - 1.0) < 1e-9


def test_unhealthy_store_lowers_score(tmp_path: Path) -> None:
    now = utc_now()
    store = JSONStore(tmp_path / "bad.json")
    store.save_record(
        OpenLoop(id="o1", question="unresolved?", status=OpenLoopStatus.OPEN)
    )
    store.save_record(
        Task(
            id="t1",
            title="late",
            description="x",
            owner_id="a",
            created_at=now - timedelta(days=5),
            due_at=now - timedelta(days=2),
            status=TaskStatus.IN_PROGRESS,
        )
    )
    store.save_record(
        Commitment(
            id="c1",
            owner_id="a",
            description="open",
            status=CommitmentStatus.PENDING,
        )
    )
    store.save_record(
        Decision(
            id="d1",
            title="old proposal",
            description="x",
            status=DecisionStatus.PROPOSED,
            created_at=now - timedelta(days=120),
        )
    )
    report = memory_health(store, now=now)
    assert report.score < 80.0
    assert report.grade in {"B", "C", "D", "F"}
    assert report.recommendations


def test_score_is_deterministic(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(OpenLoop(id="o1", question="q?", status=OpenLoopStatus.OPEN))
    now = utc_now()
    first = memory_health(store, now=now)
    second = memory_health(store, now=now)
    assert first.score == second.score
    assert first.grade == second.grade
