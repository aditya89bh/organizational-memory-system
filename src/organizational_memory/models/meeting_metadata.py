"""Structured metadata models for meetings."""

from dataclasses import dataclass, field
from enum import StrEnum


class MeetingSource(StrEnum):
    """Where a meeting record originated."""

    TRANSCRIPT = "transcript"
    MANUAL_NOTES = "manual_notes"
    IMPORTED_MARKDOWN = "imported_markdown"


class MeetingType(StrEnum):
    """The kind of meeting that took place."""

    BOARD_MEETING = "board_meeting"
    SPRINT_PLANNING = "sprint_planning"
    PRODUCT_REVIEW = "product_review"
    GENERAL = "general"


@dataclass(frozen=True, kw_only=True)
class MeetingMetadata:
    """Structured descriptive metadata for a meeting.

    Attributes:
        source: Origin of the meeting record.
        meeting_type: Category of the meeting.
        location: Optional physical or virtual location.
        tags: Free-form tags describing the meeting.
        attributes: Additional string key/value attributes.
    """

    source: MeetingSource
    meeting_type: MeetingType = MeetingType.GENERAL
    location: str | None = None
    tags: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
