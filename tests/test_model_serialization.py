"""Comprehensive serialization round-trip tests for all Phase 2 models."""

import json
from datetime import UTC, datetime

import pytest

from organizational_memory.models import (
    ActionItem,
    Assignment,
    AuditMetadata,
    Commitment,
    Decision,
    DecisionStatus,
    Dependency,
    DependencyStatus,
    DiscussionTopic,
    EntityRef,
    EntityRelationship,
    Meeting,
    MeetingMetadata,
    MeetingSource,
    MeetingType,
    MemoryEvent,
    OpenLoop,
    OwnerRef,
    OwnershipChange,
    Participant,
    Priority,
    RelationshipType,
    Risk,
    RiskStatus,
    Severity,
    Task,
    TaskStatus,
    TimelineEntry,
)
from organizational_memory.persistence import from_dict, to_dict

_WHEN = datetime(2026, 6, 24, 9, 0, tzinfo=UTC)
_LATER = datetime(2026, 7, 1, 9, 0, tzinfo=UTC)

_INSTANCES: list[object] = [
    Meeting(title="Kickoff", started_at=_WHEN, ended_at=_LATER, participants=["a"]),
    Participant(name="Alice", email="alice@example.com", role="PM"),
    Decision(
        title="Adopt CI",
        description="Use GitHub Actions",
        owner_id="alice",
        decided_at=_WHEN,
        status=DecisionStatus.ACCEPTED,
    ),
    Commitment(owner_id="bob", description="Ship report", due_at=_LATER),
    Task(
        title="Write docs",
        description="Draft docs",
        owner_id="alice",
        due_at=_LATER,
        priority=Priority.HIGH,
        status=TaskStatus.IN_PROGRESS,
    ),
    OpenLoop(question="Who owns billing?", due_at=_LATER),
    Dependency(
        source_id="t1",
        target_id="t2",
        status=DependencyStatus.RESOLVED,
    ),
    Risk(
        title="Vendor delay",
        description="May slip",
        severity=Severity.HIGH,
        status=RiskStatus.MITIGATED,
    ),
    DiscussionTopic(title="Roadmap", started_at=_WHEN, ended_at=_LATER),
    ActionItem(description="Follow up", due_at=_LATER),
    MemoryEvent(
        event_type="task.updated",
        entity_type="task",
        entity_id="t1",
        occurred_at=_WHEN,
        payload={"status": "done"},
    ),
    Assignment(entity_type="task", entity_id="t1", owner_id="alice"),
    OwnershipChange(entity_type="task", entity_id="t1", new_owner_id="bob"),
    EntityRelationship(
        source=EntityRef(entity_type="decision", entity_id="d1"),
        target=EntityRef(entity_type="task", entity_id="t1"),
        relationship_type=RelationshipType.DECISION_TO_TASK,
    ),
    OwnerRef(owner_id="alice", display_name="Alice"),
    MeetingMetadata(
        source=MeetingSource.TRANSCRIPT,
        meeting_type=MeetingType.SPRINT_PLANNING,
        tags=["q3"],
    ),
    AuditMetadata(created_by="alice", trace_id="trace-1"),
    TimelineEntry(
        timestamp=_WHEN,
        title="Decision recorded",
        entity_type="decision",
        entity_id="d1",
    ),
]


@pytest.mark.parametrize("instance", _INSTANCES, ids=lambda obj: type(obj).__name__)
def test_model_round_trips_through_dict(instance: object) -> None:
    restored = from_dict(type(instance), to_dict(instance))
    assert restored == instance


@pytest.mark.parametrize("instance", _INSTANCES, ids=lambda obj: type(obj).__name__)
def test_model_dict_is_json_serializable(instance: object) -> None:
    payload = json.dumps(to_dict(instance))
    assert isinstance(payload, str)


def test_enums_survive_round_trip() -> None:
    task = Task(title="T", description="D", owner_id="a", status=TaskStatus.DONE)
    restored = from_dict(Task, to_dict(task))
    assert restored.status is TaskStatus.DONE


def test_timestamps_survive_round_trip() -> None:
    meeting = Meeting(title="Kickoff", started_at=_WHEN)
    restored = from_dict(Meeting, to_dict(meeting))
    assert restored.started_at == _WHEN
