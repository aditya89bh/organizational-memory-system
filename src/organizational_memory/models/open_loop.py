"""Open loop domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.schemas import BaseRecord


@dataclass(kw_only=True)
class OpenLoop(BaseRecord):
    """An unresolved question or pending issue.

    The :attr:`created_at` timestamp is inherited from
    :class:`~organizational_memory.schemas.BaseRecord`.

    Attributes:
        question: The unresolved question or issue.
        owner_id: Identifier of the participant responsible for resolving it.
        status: Lifecycle status of the open loop.
        due_at: UTC timestamp by which resolution is expected, if any.
        source_meeting_id: Meeting the open loop originated from, if any.
        metadata: Free-form string key/value annotations.
    """

    question: str
    owner_id: str | None = None
    status: str = "open"
    due_at: datetime | None = None
    source_meeting_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
