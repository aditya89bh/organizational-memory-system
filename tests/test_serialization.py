"""Tests for serialization helpers."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from organizational_memory.utils.serialization import (
    from_json,
    to_json,
    to_serializable,
)


class Priority(Enum):
    LOW = "low"
    HIGH = "high"


@dataclass
class Sample:
    name: str
    created_at: datetime
    location: Path
    priority: Priority
    tags: frozenset[str] = field(default_factory=frozenset)


def _make_sample() -> Sample:
    return Sample(
        name="kickoff",
        created_at=datetime(2026, 6, 24, 9, 0, tzinfo=timezone.utc),
        location=Path("/tmp/x"),
        priority=Priority.HIGH,
        tags=frozenset({"b", "a"}),
    )


def test_to_serializable_converts_nested_types() -> None:
    result = to_serializable(_make_sample())
    assert result == {
        "name": "kickoff",
        "created_at": "2026-06-24T09:00:00Z",
        "location": "/tmp/x",
        "priority": "high",
        "tags": ["a", "b"],
    }


def test_to_json_round_trips_through_from_json() -> None:
    payload = to_json(_make_sample(), sort_keys=True)
    restored = from_json(payload)
    assert restored["priority"] == "high"
    assert restored["tags"] == ["a", "b"]


def test_to_json_supports_indent() -> None:
    text = to_json({"a": 1}, indent=2)
    assert text == '{\n  "a": 1\n}'
