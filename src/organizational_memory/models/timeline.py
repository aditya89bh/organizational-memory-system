"""Timeline models for ordering organizational memory events."""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.validation import require_non_empty


@dataclass(frozen=True, kw_only=True)
class TimelineEntry:
    """A single dated entry on an organizational timeline.

    Attributes:
        timestamp: UTC timestamp the entry is positioned at.
        title: Short label for the entry.
        entity_type: Type of entity the entry refers to.
        entity_id: Identifier of the referenced entity.
        description: Optional longer description.
        metadata: Free-form string key/value annotations.
    """

    timestamp: datetime
    title: str
    entity_type: str
    entity_id: str
    description: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_non_empty(self.title, "title")
        require_non_empty(self.entity_type, "entity_type")
        require_non_empty(self.entity_id, "entity_id")


@dataclass
class OrganizationalTimeline:
    """An ordered collection of timeline entries.

    Attributes:
        entries: The timeline entries, in insertion order.
    """

    entries: list[TimelineEntry] = field(default_factory=list)

    def add(self, entry: TimelineEntry) -> None:
        """Append ``entry`` to the timeline."""
        self.entries.append(entry)

    def ordered(self) -> list[TimelineEntry]:
        """Return the entries sorted by ascending timestamp."""
        return sorted(self.entries, key=lambda entry: entry.timestamp)

    def __len__(self) -> int:
        return len(self.entries)
