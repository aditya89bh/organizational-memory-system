"""Action item domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.schemas import BaseRecord
from organizational_memory.validation import require_non_empty, validate_due_after


@dataclass(kw_only=True)
class ActionItem(BaseRecord):
    """A lightweight follow-up item extracted from a discussion.

    Attributes:
        description: What needs to be done.
        owner_id: Identifier of the participant responsible, if assigned.
        due_at: UTC timestamp by which the item is due, if any.
        status: Lifecycle status of the action item.
        source_meeting_id: Meeting the item originated from, if any.
        metadata: Free-form string key/value annotations.
    """

    description: str
    owner_id: str | None = None
    due_at: datetime | None = None
    status: str = "open"
    source_meeting_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_non_empty(self.description, "description")
        validate_due_after(self.created_at, self.due_at)
