"""Tests for persistence conversion helpers."""

from datetime import UTC, datetime

import pytest

from organizational_memory.exceptions import ValidationError
from organizational_memory.models import (
    Decision,
    DecisionStatus,
    EntityRef,
    EntityRelationship,
    Meeting,
    MeetingMetadata,
    MeetingSource,
    MemoryEvent,
    RelationshipType,
)
from organizational_memory.persistence import from_dict, to_dict


def test_to_dict_requires_dataclass_instance() -> None:
    with pytest.raises(TypeError, match="dataclass instance"):
        to_dict({"not": "a dataclass"})


def test_decision_round_trip() -> None:
    decision = Decision(
        title="Adopt CI",
        description="Use GitHub Actions",
        owner_id="alice",
        decided_at=datetime(2026, 6, 24, 9, 0, tzinfo=UTC),
        status=DecisionStatus.ACCEPTED,
    )
    restored = from_dict(Decision, to_dict(decision))
    assert restored == decision
    assert restored.status is DecisionStatus.ACCEPTED


def test_meeting_round_trip_with_optional_none() -> None:
    meeting = Meeting(title="Kickoff", started_at=datetime(2026, 6, 24, 9, tzinfo=UTC))
    restored = from_dict(Meeting, to_dict(meeting))
    assert restored == meeting
    assert restored.ended_at is None


def test_memory_event_round_trip_preserves_payload() -> None:
    event = MemoryEvent(
        event_type="task.updated",
        entity_type="task",
        entity_id="t1",
        payload={"status": "done", "version": 2},
    )
    restored = from_dict(MemoryEvent, to_dict(event))
    assert restored == event
    assert restored.payload["version"] == 2


def test_nested_relationship_round_trip() -> None:
    relationship = EntityRelationship(
        source=EntityRef(entity_type="decision", entity_id="d1"),
        target=EntityRef(entity_type="task", entity_id="t1"),
        relationship_type=RelationshipType.DECISION_TO_TASK,
    )
    restored = from_dict(EntityRelationship, to_dict(relationship))
    assert restored == relationship
    assert restored.source.entity_id == "d1"


def test_meeting_metadata_round_trip() -> None:
    metadata = MeetingMetadata(
        source=MeetingSource.TRANSCRIPT,
        tags=["q3", "planning"],
        attributes={"recorder": "alice"},
    )
    restored = from_dict(MeetingMetadata, to_dict(metadata))
    assert restored == metadata


def test_from_dict_rejects_invalid_enum_value() -> None:
    data = to_dict(Decision(title="X", description="Y"))
    data["status"] = "not-a-status"
    with pytest.raises(ValidationError, match="Cannot build Decision"):
        from_dict(Decision, data)
