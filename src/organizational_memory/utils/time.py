"""Timezone-aware timestamp utilities.

The system stores all timestamps in UTC and serializes them as ISO 8601 strings
using a trailing ``Z`` designator.
"""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(UTC)


def format_timestamp(value: datetime) -> str:
    """Format a timezone-aware datetime as an ISO 8601 UTC string.

    Raises:
        ValueError: If ``value`` is naive (has no timezone information).
    """
    if value.tzinfo is None:
        raise ValueError("Cannot format a naive datetime; timezone info is required.")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO 8601 string into a timezone-aware UTC datetime.

    Naive inputs are assumed to be UTC. A trailing ``Z`` designator is accepted.

    Raises:
        ValueError: If ``value`` is not a valid ISO 8601 timestamp.
    """
    text = value.strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO 8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
