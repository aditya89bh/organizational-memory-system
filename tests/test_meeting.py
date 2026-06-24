"""Tests for the Meeting model."""

from datetime import UTC, datetime

import pytest

from organizational_memory.models import Meeting


def _started() -> datetime:
    return datetime(2026, 6, 24, 9, 0, tzinfo=UTC)


def test_meeting_construction_defaults() -> None:
    meeting = Meeting(title="Sprint Planning", started_at=_started())
    assert meeting.title == "Sprint Planning"
    assert meeting.ended_at is None
    assert meeting.participants == []
    assert meeting.source == "unknown"
    assert meeting.id


def test_meeting_with_participants_and_metadata() -> None:
    meeting = Meeting(
        title="Board Review",
        started_at=_started(),
        ended_at=datetime(2026, 6, 24, 10, 0, tzinfo=UTC),
        participants=["alice", "bob"],
        source="transcript",
        metadata={"room": "A1"},
    )
    assert meeting.participants == ["alice", "bob"]
    assert meeting.metadata["room"] == "A1"


def test_meeting_rejects_invalid_time_range() -> None:
    with pytest.raises(ValueError, match="ended_at cannot be before started_at"):
        Meeting(
            title="Bad",
            started_at=_started(),
            ended_at=datetime(2026, 6, 24, 8, 0, tzinfo=UTC),
        )


def test_meeting_serialization_round_trip_dict() -> None:
    meeting = Meeting(title="Kickoff", started_at=_started())
    data = meeting.to_dict()
    assert data["title"] == "Kickoff"
    assert data["started_at"] == "2026-06-24T09:00:00Z"
