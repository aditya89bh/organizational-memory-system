"""Importance ranking from deterministic record fields.

Importance combines a record-type weight, a severity/priority level, and a
status weight (active items rank above terminal ones). An explicit
``metadata["importance"]`` value, when present and numeric, overrides the
computed score.
"""

from organizational_memory.recall.filters import status_value
from organizational_memory.schemas.base import BaseRecord

TYPE_WEIGHTS: dict[str, float] = {
    "Decision": 1.0,
    "Risk": 0.9,
    "Commitment": 0.8,
    "Task": 0.7,
    "OpenLoop": 0.6,
    "ActionItem": 0.6,
    "Dependency": 0.5,
    "Meeting": 0.5,
    "DiscussionTopic": 0.4,
    "MemoryEvent": 0.4,
    "Participant": 0.3,
}

LEVEL_WEIGHTS: dict[str, float] = {
    "low": 0.25,
    "medium": 0.5,
    "high": 0.75,
    "critical": 1.0,
    "urgent": 1.0,
}

_ACTIVE_STATUSES = frozenset(
    {"open", "pending", "in_progress", "blocked", "todo", "identified", "proposed"}
)
_TERMINAL_STATUSES = frozenset(
    {
        "resolved",
        "done",
        "completed",
        "closed",
        "mitigated",
        "cancelled",
        "dismissed",
        "rejected",
        "superseded",
        "accepted",
    }
)

_TYPE_WEIGHT = 0.4
_LEVEL_WEIGHT = 0.3
_STATUS_WEIGHT = 0.3
_DEFAULT_TYPE_WEIGHT = 0.3


def _type_weight(record: BaseRecord) -> float:
    return TYPE_WEIGHTS.get(type(record).__name__, _DEFAULT_TYPE_WEIGHT)


def _level_weight(record: BaseRecord) -> float:
    value = getattr(record, "severity", None) or getattr(record, "priority", None)
    if value is None:
        return 0.5
    return LEVEL_WEIGHTS.get(status_value(value), 0.5)


def _status_weight(record: BaseRecord) -> float:
    status = getattr(record, "status", None)
    if status is None:
        return 0.6
    value = status_value(status)
    if value in _ACTIVE_STATUSES:
        return 1.0
    if value in _TERMINAL_STATUSES:
        return 0.4
    return 0.6


def _explicit_override(record: BaseRecord) -> float | None:
    metadata = getattr(record, "metadata", {})
    raw = metadata.get("importance") if isinstance(metadata, dict) else None
    if raw is None:
        return None
    try:
        return max(0.0, min(1.0, float(raw)))
    except (TypeError, ValueError):
        return None


def importance_score(record: BaseRecord) -> float:
    """Return an importance score in ``[0, 1]``; higher is more important."""
    override = _explicit_override(record)
    if override is not None:
        return round(override, 6)
    score = (
        _TYPE_WEIGHT * _type_weight(record)
        + _LEVEL_WEIGHT * _level_weight(record)
        + _STATUS_WEIGHT * _status_weight(record)
    )
    return round(score, 6)
