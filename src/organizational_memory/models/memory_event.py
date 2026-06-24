"""Memory event domain model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from organizational_memory.schemas import BaseRecord
from organizational_memory.utils.time import utc_now


@dataclass(kw_only=True)
class MemoryEvent(BaseRecord):
    """An append-only event describing a change to organizational memory.

    Attributes:
        event_type: What happened (e.g. ``"decision.created"``).
        entity_type: Type of entity the event concerns (e.g. ``"decision"``).
        entity_id: Identifier of the affected entity.
        occurred_at: UTC timestamp when the event occurred.
        actor_id: Identifier of the participant who triggered the event.
        payload: JSON-compatible details about the event.
        metadata: Free-form string key/value annotations.
    """

    event_type: str
    entity_type: str
    entity_id: str
    occurred_at: datetime = field(default_factory=utc_now)
    actor_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)
