"""Tests for the Task model."""

from datetime import UTC, datetime

from organizational_memory.models import Task


def test_task_defaults() -> None:
    task = Task(title="Write docs", description="Draft the schema docs", owner_id="a")
    assert task.priority == "medium"
    assert task.status == "todo"
    assert task.due_at is None


def test_task_full_construction() -> None:
    task = Task(
        title="Write docs",
        description="Draft the schema docs",
        owner_id="bob",
        due_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
        priority="high",
        status="in_progress",
        source_meeting_id="m1",
        metadata={"epic": "docs"},
    )
    assert task.priority == "high"
    assert task.status == "in_progress"


def test_task_serialization() -> None:
    task = Task(title="Write docs", description="Draft", owner_id="a")
    data = task.to_dict()
    assert data["title"] == "Write docs"
    assert data["priority"] == "medium"
