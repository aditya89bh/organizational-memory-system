"""Deterministic, rule-based extraction of organizational memory records."""

from organizational_memory.extraction.normalization import (
    normalize_bullets,
    normalize_text,
    normalize_whitespace,
    shorten,
    strip_timestamps,
)
from organizational_memory.extraction.speakers import (
    SpeakerMatch,
    SpeakerTurn,
    match_speaker,
    parse_speaker_turns,
)

__all__ = [
    "SpeakerMatch",
    "SpeakerTurn",
    "match_speaker",
    "normalize_bullets",
    "normalize_text",
    "normalize_whitespace",
    "parse_speaker_turns",
    "shorten",
    "strip_timestamps",
]
