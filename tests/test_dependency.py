"""Tests for the Dependency model."""

from organizational_memory.models import Dependency


def test_dependency_defaults() -> None:
    dependency = Dependency(source_id="task-1", target_id="task-2")
    assert dependency.dependency_type == "blocks"
    assert dependency.status == "pending"
    assert dependency.description is None


def test_dependency_full_construction() -> None:
    dependency = Dependency(
        source_id="task-1",
        target_id="task-2",
        dependency_type="requires",
        description="Task 1 requires Task 2",
        status="resolved",
        metadata={"severity": "high"},
    )
    assert dependency.dependency_type == "requires"
    assert dependency.status == "resolved"


def test_dependency_serialization() -> None:
    dependency = Dependency(source_id="a", target_id="b")
    data = dependency.to_dict()
    assert data["source_id"] == "a"
    assert data["target_id"] == "b"
