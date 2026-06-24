"""Tests for the Task model."""

from datetime import UTC, datetime

from organizational_memory.models import Priority, Task, TaskStatus


def test_task_defaults() -> None:
    task = Task(title="Write docs", description="Draft the schema docs", owner_id="a")
    assert task.priority is Priority.MEDIUM
    assert task.status is TaskStatus.TODO
    assert task.due_at is None


def test_task_full_construction() -> None:
    task = Task(
        title="Write docs",
        description="Draft the schema docs",
        owner_id="bob",
        due_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
        priority=Priority.HIGH,
        status=TaskStatus.IN_PROGRESS,
        source_meeting_id="m1",
        metadata={"epic": "docs"},
    )
    assert task.priority is Priority.HIGH
    assert task.status is TaskStatus.IN_PROGRESS


def test_task_serialization() -> None:
    task = Task(title="Write docs", description="Draft", owner_id="a")
    data = task.to_dict()
    assert data["title"] == "Write docs"
    assert data["priority"] == "medium"
    assert data["status"] == "todo"
