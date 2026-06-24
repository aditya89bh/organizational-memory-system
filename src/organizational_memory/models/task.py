"""Task domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.models.enums import Priority, TaskStatus
from organizational_memory.schemas import BaseRecord
from organizational_memory.validation import (
    require_non_empty,
    require_owner,
    validate_due_after,
)


@dataclass(kw_only=True)
class Task(BaseRecord):
    """A unit of work owned by a participant.

    Attributes:
        title: Short task title.
        description: Fuller description of the work.
        owner_id: Identifier of the participant responsible for the task.
        due_at: UTC timestamp by which the task is due, if any.
        priority: Relative importance of the task.
        status: Lifecycle status of the task.
        source_meeting_id: Meeting the task originated from, if any.
        metadata: Free-form string key/value annotations.
    """

    title: str
    description: str
    owner_id: str
    due_at: datetime | None = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    source_meeting_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_non_empty(self.title, "title")
        require_non_empty(self.description, "description")
        require_owner(self.owner_id)
        validate_due_after(self.created_at, self.due_at)
