"""Meeting domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.schemas import BaseRecord


@dataclass(kw_only=True)
class Meeting(BaseRecord):
    """A meeting from which organizational memory is extracted.

    Attributes:
        title: Human-readable meeting title.
        started_at: UTC timestamp when the meeting started.
        ended_at: UTC timestamp when the meeting ended, if known.
        participants: Identifiers or names of attendees.
        source: Where the meeting record originated (e.g. ``"transcript"``).
        metadata: Free-form string key/value annotations.
    """

    title: str
    started_at: datetime
    ended_at: datetime | None = None
    participants: list[str] = field(default_factory=list)
    source: str = "unknown"
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.ended_at is not None and self.ended_at < self.started_at:
            raise ValueError("Meeting ended_at cannot be before started_at.")
