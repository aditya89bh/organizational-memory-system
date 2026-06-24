"""Commitment domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.models.enums import CommitmentStatus
from organizational_memory.schemas import BaseRecord
from organizational_memory.validation import (
    require_non_empty,
    require_owner,
    validate_due_after,
)


@dataclass(kw_only=True)
class Commitment(BaseRecord):
    """A promise made by someone to deliver something.

    The :attr:`created_at` timestamp is inherited from
    :class:`~organizational_memory.schemas.BaseRecord`.

    Attributes:
        owner_id: Identifier of the participant who made the commitment.
        description: What was committed to.
        due_at: UTC timestamp by which the commitment is due, if any.
        status: Lifecycle status of the commitment.
        source_meeting_id: Meeting the commitment originated from, if any.
        metadata: Free-form string key/value annotations.
    """

    owner_id: str
    description: str
    due_at: datetime | None = None
    status: CommitmentStatus = CommitmentStatus.PENDING
    source_meeting_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_owner(self.owner_id)
        require_non_empty(self.description, "description")
        validate_due_after(self.created_at, self.due_at)
