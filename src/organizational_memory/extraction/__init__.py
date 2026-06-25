"""Deterministic, rule-based extraction of organizational memory records."""

from organizational_memory.extraction.normalization import (
    normalize_bullets,
    normalize_text,
    normalize_whitespace,
    shorten,
    strip_timestamps,
)
from organizational_memory.extraction.segmentation import (
    Segment,
    SegmentKind,
    segment_text,
    segment_transcript,
)
from organizational_memory.extraction.speakers import (
    SpeakerMatch,
    SpeakerTurn,
    match_speaker,
    parse_speaker_turns,
)

__all__ = [
    "Segment",
    "SegmentKind",
    "SpeakerMatch",
    "SpeakerTurn",
    "match_speaker",
    "normalize_bullets",
    "normalize_text",
    "normalize_whitespace",
    "parse_speaker_turns",
    "segment_text",
    "segment_transcript",
    "shorten",
    "strip_timestamps",
]
