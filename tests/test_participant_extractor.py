"""Tests for the participant extractor."""

from organizational_memory.extraction.participant_extractor import (
    extract_participants,
)
from organizational_memory.extraction.segmentation import segment_text

SAMPLE = """Attendees: Alice, Bob and Carol
Alice: Let's begin.
Dave: I joined late.
"""


def test_extracts_from_attendee_line_and_speakers() -> None:
    participants = extract_participants(segment_text(SAMPLE))
    names = [p.name for p in participants]
    assert names == ["Alice", "Bob", "Carol", "Dave"]


def test_deduplicates_speaker_and_attendee() -> None:
    participants = extract_participants(segment_text(SAMPLE))
    assert sum(1 for p in participants if p.name == "Alice") == 1


def test_attendee_provenance() -> None:
    participants = extract_participants(segment_text("Participants: Alice, Bob"))
    assert participants[0].metadata["matched_phrase"] == "attendee_line"


def test_no_participants() -> None:
    assert extract_participants(segment_text("- a plain bullet\nplain text")) == []
