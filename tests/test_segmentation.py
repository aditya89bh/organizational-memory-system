"""Tests for transcript segmentation."""

from organizational_memory.extraction.segmentation import (
    SegmentKind,
    segment_text,
    segment_transcript,
)
from organizational_memory.ingestion.transcript_loader import (
    Transcript,
    TranscriptFormat,
)

SAMPLE = """# Sprint Planning

Alice: We should ship on Friday.
- prepare the release notes
1. review metrics

This is a plain paragraph.
"""


def test_segment_kinds() -> None:
    segments = segment_text(SAMPLE)
    kinds = [seg.kind for seg in segments]
    assert kinds == [
        SegmentKind.HEADING,
        SegmentKind.SPEAKER_TURN,
        SegmentKind.BULLET,
        SegmentKind.BULLET,
        SegmentKind.PARAGRAPH,
    ]


def test_segment_ids_are_sequential() -> None:
    segments = segment_text(SAMPLE)
    assert [seg.id for seg in segments] == [f"seg-{i}" for i in range(1, 6)]


def test_speaker_segment_captures_speaker() -> None:
    segments = segment_text(SAMPLE)
    speaker_segment = next(
        seg for seg in segments if seg.kind is SegmentKind.SPEAKER_TURN
    )
    assert speaker_segment.speaker == "Alice"
    assert speaker_segment.text == "We should ship on Friday."


def test_heading_strips_hashes() -> None:
    segments = segment_text(SAMPLE)
    assert segments[0].text == "Sprint Planning"


def test_line_numbers_preserved() -> None:
    segments = segment_text(SAMPLE)
    assert segments[0].line_number == 1
    assert segments[1].line_number == 3


def test_segment_transcript() -> None:
    transcript = Transcript(text=SAMPLE, content_format=TranscriptFormat.MARKDOWN)
    assert len(segment_transcript(transcript)) == 5
