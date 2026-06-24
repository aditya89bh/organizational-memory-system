"""Relationship schemas linking domain entities."""

from dataclasses import dataclass, field
from enum import StrEnum

from organizational_memory.schemas import BaseRecord
from organizational_memory.validation import require_non_empty


class RelationshipType(StrEnum):
    """Supported relationship types between domain entities."""

    DECISION_TO_TASK = "decision_to_task"
    DECISION_TO_COMMITMENT = "decision_to_commitment"
    TASK_BLOCKS_TASK = "task_blocks_task"
    RISK_AFFECTS_DECISION = "risk_affects_decision"
    OPEN_LOOP_BLOCKS_DECISION = "open_loop_blocks_decision"


@dataclass(frozen=True, kw_only=True)
class EntityRef:
    """A typed reference to a domain entity.

    Attributes:
        entity_type: Type of the referenced entity (e.g. ``"decision"``).
        entity_id: Identifier of the referenced entity.
    """

    entity_type: str
    entity_id: str

    def __post_init__(self) -> None:
        require_non_empty(self.entity_type, "entity_type")
        require_non_empty(self.entity_id, "entity_id")


@dataclass(kw_only=True)
class EntityRelationship(BaseRecord):
    """A directed, typed relationship between two entities.

    Attributes:
        source: The originating entity.
        target: The related entity.
        relationship_type: The kind of relationship.
        description: Optional human-readable explanation.
        metadata: Free-form string key/value annotations.
    """

    source: EntityRef
    target: EntityRef
    relationship_type: RelationshipType
    description: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
