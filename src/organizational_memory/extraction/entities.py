"""Conservative, deterministic entity extraction.

This module surfaces three kinds of lightweight entities: person-like names
taken from speaker turns, date-like phrases matched by fixed patterns, and
capitalized multi-word phrases that look like project or topic names.
"""

import re
from collections.abc import Iterable
from dataclasses import dataclass, field

from organizational_memory.extraction.segmentation import Segment

_WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)
_MONTHS = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)

_DATE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"\b(?:" + "|".join(_MONTHS) + r")\s+\d{1,2}(?:st|nd|rd|th)?\b", re.I),
    re.compile(r"\b(?:" + "|".join(_WEEKDAYS) + r")\b", re.I),
    re.compile(r"\b(?:today|tomorrow|yesterday)\b", re.I),
    re.compile(r"\bnext\s+(?:week|month|quarter|year)\b", re.I),
    re.compile(r"\bq[1-4]\b", re.I),
)

_CAPITALIZED_PHRASE = re.compile(
    r"\b[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)+\b"
)


@dataclass(frozen=True)
class ExtractedEntities:
    """A bundle of conservatively extracted entities."""

    persons: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(value)
    return ordered


def extract_persons(segments: Iterable[Segment]) -> list[str]:
    """Return unique speaker names from speaker turns, in order."""
    return _unique(seg.speaker for seg in segments if seg.speaker)


def extract_dates(text: str) -> list[str]:
    """Return unique date-like phrases found in ``text``, in order."""
    matches: list[tuple[int, str]] = []
    for pattern in _DATE_PATTERNS:
        matches.extend((m.start(), m.group(0)) for m in pattern.finditer(text))
    ordered = [value for _, value in sorted(matches, key=lambda item: item[0])]
    return _unique(ordered)


def extract_capitalized_phrases(text: str) -> list[str]:
    """Return unique capitalized multi-word phrases that look like topics."""
    return _unique(match.group(0) for match in _CAPITALIZED_PHRASE.finditer(text))


def extract_entities(segments: Iterable[Segment], text: str) -> ExtractedEntities:
    """Extract persons, dates, and topic-like phrases."""
    segment_list = list(segments)
    return ExtractedEntities(
        persons=extract_persons(segment_list),
        dates=extract_dates(text),
        topics=extract_capitalized_phrases(text),
    )
