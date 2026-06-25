"""Split normalized transcripts into typed segments for extraction."""

import re
from dataclasses import dataclass
from enum import StrEnum

from organizational_memory.extraction.speakers import match_speaker
from organizational_memory.ingestion.transcript_loader import Transcript

_HEADING = re.compile(r"^\s*#{1,6}\s+(?P<text>\S.*)$")
_BULLET = re.compile(r"^\s*[-*+]\s+(?P<text>\S.*)$")
_NUMBERED = re.compile(r"^\s*\d+[.)]\s+(?P<text>\S.*)$")


class SegmentKind(StrEnum):
    """The structural role of a transcript segment."""

    HEADING = "heading"
    SPEAKER_TURN = "speaker_turn"
    BULLET = "bullet"
    PARAGRAPH = "paragraph"


@dataclass(frozen=True)
class Segment:
    """A single classified unit of transcript text.

    Attributes:
        id: Stable identifier of the form ``seg-<n>``.
        kind: The structural role of the segment.
        text: The meaningful text content of the segment.
        line_number: 1-based line number in the source text.
        speaker: Speaker name when the segment is a speaker turn.
    """

    id: str
    kind: SegmentKind
    text: str
    line_number: int
    speaker: str | None = None


def _classify(line: str) -> tuple[SegmentKind, str, str | None]:
    heading = _HEADING.match(line)
    if heading is not None:
        return SegmentKind.HEADING, heading.group("text").strip(), None

    speaker = match_speaker(line)
    if speaker is not None:
        return SegmentKind.SPEAKER_TURN, speaker.text, speaker.speaker

    bullet = _BULLET.match(line) or _NUMBERED.match(line)
    if bullet is not None:
        return SegmentKind.BULLET, bullet.group("text").strip(), None

    return SegmentKind.PARAGRAPH, line.strip(), None


def segment_text(text: str) -> list[Segment]:
    """Split raw ``text`` into typed segments, one per non-blank line."""
    segments: list[Segment] = []
    counter = 0
    for index, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        kind, content, speaker = _classify(line)
        if not content:
            continue
        counter += 1
        segments.append(
            Segment(
                id=f"seg-{counter}",
                kind=kind,
                text=content,
                line_number=index,
                speaker=speaker,
            )
        )
    return segments


def segment_transcript(transcript: Transcript) -> list[Segment]:
    """Split a :class:`Transcript` into typed segments."""
    return segment_text(transcript.text)
