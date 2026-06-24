"""Ownership primitives for domain records.

These models track who owns decisions, commitments, tasks, risks, and open loops
and record changes in ownership over time.
"""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.schemas import BaseRecord
from organizational_memory.utils.time import utc_now
from organizational_memory.validation import require_non_empty, require_owner


@dataclass(frozen=True, kw_only=True)
class OwnerRef:
    """A lightweight reference to an owning participant.

    Attributes:
        owner_id: Identifier of the owning participant.
        display_name: Optional human-readable owner name.
    """

    owner_id: str
    display_name: str | None = None

    def __post_init__(self) -> None:
        require_owner(self.owner_id)


@dataclass(kw_only=True)
class Assignment(BaseRecord):
    """An assignment of an entity to an owner.

    Attributes:
        entity_type: Type of the owned entity (e.g. ``"task"``).
        entity_id: Identifier of the owned entity.
        owner_id: Identifier of the assigned owner.
        role: Optional role the owner plays for this entity.
        assigned_at: UTC timestamp when the assignment was made.
        metadata: Free-form string key/value annotations.
    """

    entity_type: str
    entity_id: str
    owner_id: str
    role: str | None = None
    assigned_at: datetime = field(default_factory=utc_now)
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_non_empty(self.entity_type, "entity_type")
        require_non_empty(self.entity_id, "entity_id")
        require_owner(self.owner_id)


@dataclass(kw_only=True)
class OwnershipChange(BaseRecord):
    """A record of an entity changing owners.

    Attributes:
        entity_type: Type of the affected entity.
        entity_id: Identifier of the affected entity.
        new_owner_id: Identifier of the new owner.
        previous_owner_id: Identifier of the previous owner, if any.
        changed_at: UTC timestamp when ownership changed.
        reason: Optional explanation for the change.
        metadata: Free-form string key/value annotations.
    """

    entity_type: str
    entity_id: str
    new_owner_id: str
    previous_owner_id: str | None = None
    changed_at: datetime = field(default_factory=utc_now)
    reason: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_non_empty(self.entity_type, "entity_type")
        require_non_empty(self.entity_id, "entity_id")
        require_owner(self.new_owner_id, "new_owner_id")
