"""Participant domain model."""

from dataclasses import dataclass, field

from organizational_memory.schemas import BaseRecord


@dataclass(kw_only=True)
class Participant(BaseRecord):
    """A person who took part in a meeting or owns memory records.

    Attributes:
        name: Display name of the participant.
        email: Contact email address, if known.
        role: Role played in the organization or meeting.
        organization: Organization the participant belongs to.
        metadata: Free-form string key/value annotations.
    """

    name: str
    email: str | None = None
    role: str | None = None
    organization: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
