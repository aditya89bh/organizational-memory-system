"""Recency ranking based on a record's most relevant timestamp.

The score decays exponentially with the age of the most recent relevant
timestamp, so newer records rank higher. The decay is controlled by a
configurable half-life and is fully deterministic for a fixed reference time.
"""

from datetime import datetime

from organizational_memory.schemas.base import BaseRecord
from organizational_memory.utils.time import utc_now

_TIMESTAMP_FIELDS = (
    "created_at",
    "updated_at",
    "decided_at",
    "due_at",
    "occurred_at",
    "started_at",
)

DEFAULT_HALF_LIFE_DAYS = 30.0


def relevant_timestamp(record: BaseRecord) -> datetime:
    """Return the most recent relevant timestamp on ``record``.

    Considers created/updated/decided/due/occurred/started timestamps and
    returns the latest one present, falling back to ``created_at``.
    """
    moments = [
        value
        for field_name in _TIMESTAMP_FIELDS
        if isinstance(value := getattr(record, field_name, None), datetime)
    ]
    return max(moments) if moments else record.created_at


def recency_score(
    record: BaseRecord,
    *,
    now: datetime | None = None,
    half_life_days: float = DEFAULT_HALF_LIFE_DAYS,
) -> float:
    """Return a recency score in ``(0, 1]``; newer records score higher.

    A record whose reference timestamp is at (or after) ``now`` scores ``1.0``;
    older records decay by half every ``half_life_days``.
    """
    if half_life_days <= 0:
        raise ValueError("half_life_days must be positive")
    reference = now or utc_now()
    age_seconds = (reference - relevant_timestamp(record)).total_seconds()
    age_days = max(0.0, age_seconds / 86400.0)
    decay: float = 0.5 ** (age_days / half_life_days)
    return round(decay, 6)
