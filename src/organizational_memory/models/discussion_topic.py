"""Discussion topic domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.schemas import BaseRecord
from organizational_memory.validation import require_non_empty, validate_time_range


@dataclass(kw_only=True)
class DiscussionTopic(BaseRecord):
    """A topic discussed during a meeting.

    Attributes:
        title: Short title of the topic.
        summary: Optional summary of the discussion.
        source_meeting_id: Meeting the topic was discussed in, if any.
        participant_ids: Identifiers of participants involved in the topic.
        started_at: UTC timestamp when discussion of the topic began.
        ended_at: UTC timestamp when discussion of the topic ended.
        metadata: Free-form string key/value annotations.
    """

    title: str
    summary: str | None = None
    source_meeting_id: str | None = None
    participant_ids: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_non_empty(self.title, "title")
        validate_time_range(self.started_at, self.ended_at)
