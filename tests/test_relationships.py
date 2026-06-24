"""Tests for relationship schemas."""

import pytest

from organizational_memory.exceptions import ValidationError
from organizational_memory.models import (
    EntityRef,
    EntityRelationship,
    RelationshipType,
)


def test_relationship_type_values() -> None:
    assert {member.value for member in RelationshipType} == {
        "decision_to_task",
        "decision_to_commitment",
        "task_blocks_task",
        "risk_affects_decision",
        "open_loop_blocks_decision",
    }


def test_entity_ref_rejects_blank() -> None:
    with pytest.raises(ValidationError, match="entity_id must not be empty"):
        EntityRef(entity_type="decision", entity_id="")


def test_entity_relationship_construction() -> None:
    relationship = EntityRelationship(
        source=EntityRef(entity_type="decision", entity_id="d1"),
        target=EntityRef(entity_type="task", entity_id="t1"),
        relationship_type=RelationshipType.DECISION_TO_TASK,
        description="Decision spawns task",
    )
    assert relationship.source.entity_id == "d1"
    assert relationship.target.entity_type == "task"
    assert relationship.relationship_type is RelationshipType.DECISION_TO_TASK


def test_entity_relationship_serialization() -> None:
    relationship = EntityRelationship(
        source=EntityRef(entity_type="risk", entity_id="r1"),
        target=EntityRef(entity_type="decision", entity_id="d1"),
        relationship_type=RelationshipType.RISK_AFFECTS_DECISION,
    )
    data = relationship.to_dict()
    assert data["relationship_type"] == "risk_affects_decision"
    assert data["source"]["entity_id"] == "r1"
