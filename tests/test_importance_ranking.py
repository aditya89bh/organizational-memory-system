"""Tests for importance ranking."""

from organizational_memory.models import Decision, Risk, Task
from organizational_memory.models.enums import (
    Priority,
    RiskStatus,
    Severity,
    TaskStatus,
)
from organizational_memory.recall.ranking.importance import importance_score


def test_critical_risk_outranks_low_task() -> None:
    risk = Risk(
        title="Outage",
        description="x",
        severity=Severity.CRITICAL,
        status=RiskStatus.IDENTIFIED,
    )
    task = Task(
        title="Tidy",
        description="x",
        owner_id="a",
        priority=Priority.LOW,
        status=TaskStatus.DONE,
    )
    assert importance_score(risk) > importance_score(task)


def test_active_status_outranks_terminal() -> None:
    active = Task(
        title="a", description="x", owner_id="a", status=TaskStatus.IN_PROGRESS
    )
    done = Task(title="b", description="x", owner_id="a", status=TaskStatus.DONE)
    assert importance_score(active) > importance_score(done)


def test_priority_increases_score() -> None:
    high = Task(title="a", description="x", owner_id="a", priority=Priority.URGENT)
    low = Task(title="b", description="x", owner_id="a", priority=Priority.LOW)
    assert importance_score(high) > importance_score(low)


def test_explicit_override() -> None:
    decision = Decision(
        title="x", description="y", metadata={"importance": "0.95"}
    )
    assert importance_score(decision) == 0.95


def test_invalid_override_ignored() -> None:
    decision = Decision(
        title="x", description="y", metadata={"importance": "not-a-number"}
    )
    assert 0.0 <= importance_score(decision) <= 1.0


def test_score_bounds() -> None:
    decision = Decision(title="x", description="y")
    assert 0.0 <= importance_score(decision) <= 1.0
