"""Tests for meeting metadata models."""

from organizational_memory.models import (
    MeetingMetadata,
    MeetingSource,
    MeetingType,
)


def test_meeting_source_values() -> None:
    assert {member.value for member in MeetingSource} == {
        "transcript",
        "manual_notes",
        "imported_markdown",
    }


def test_meeting_type_values() -> None:
    assert MeetingType.BOARD_MEETING.value == "board_meeting"
    assert MeetingType.SPRINT_PLANNING.value == "sprint_planning"
    assert MeetingType.PRODUCT_REVIEW.value == "product_review"


def test_meeting_metadata_defaults() -> None:
    metadata = MeetingMetadata(source=MeetingSource.TRANSCRIPT)
    assert metadata.meeting_type is MeetingType.GENERAL
    assert metadata.location is None
    assert metadata.tags == []
    assert metadata.attributes == {}


def test_meeting_metadata_full() -> None:
    metadata = MeetingMetadata(
        source=MeetingSource.MANUAL_NOTES,
        meeting_type=MeetingType.SPRINT_PLANNING,
        location="Room 1",
        tags=["q3", "planning"],
        attributes={"recorder": "alice"},
    )
    assert metadata.source is MeetingSource.MANUAL_NOTES
    assert metadata.tags == ["q3", "planning"]
    assert metadata.attributes["recorder"] == "alice"
