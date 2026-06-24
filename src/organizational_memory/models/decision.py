"""Decision domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.models.enums import DecisionStatus
from organizational_memory.schemas import BaseRecord
from organizational_memory.validation import require_non_empty


@dataclass(kw_only=True)
class Decision(BaseRecord):
    """A decision reached by the organization.

    Attributes:
        title: Short statement of the decision.
        description: Fuller description of what was decided.
        owner_id: Identifier of the participant accountable for the decision.
        rationale: Why the decision was made.
        decided_at: UTC timestamp when the decision was finalized.
        status: Lifecycle status of the decision.
        source_meeting_id: Meeting the decision originated from, if any.
        metadata: Free-form string key/value annotations.
    """

    title: str
    description: str
    owner_id: str | None = None
    rationale: str | None = None
    decided_at: datetime | None = None
    status: DecisionStatus = DecisionStatus.PROPOSED
    source_meeting_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_non_empty(self.title, "title")
        require_non_empty(self.description, "description")
