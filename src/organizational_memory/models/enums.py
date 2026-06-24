"""Status and grading enumerations for domain models.

All enumerations are string-valued so they serialize directly to JSON and can be
reconstructed from their string values.
"""

from enum import StrEnum


class DecisionStatus(StrEnum):
    """Lifecycle status of a decision."""

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class CommitmentStatus(StrEnum):
    """Lifecycle status of a commitment."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(StrEnum):
    """Lifecycle status of a task."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


class OpenLoopStatus(StrEnum):
    """Lifecycle status of an open loop."""

    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class RiskStatus(StrEnum):
    """Lifecycle status of a risk."""

    IDENTIFIED = "identified"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class DependencyStatus(StrEnum):
    """Lifecycle status of a dependency."""

    PENDING = "pending"
    RESOLVED = "resolved"
    BLOCKED = "blocked"


class Priority(StrEnum):
    """Relative importance of a task or item."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Severity(StrEnum):
    """Impact level of a risk."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Likelihood(StrEnum):
    """Probability that a risk materializes."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
