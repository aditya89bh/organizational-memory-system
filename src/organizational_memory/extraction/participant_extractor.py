"""Deterministic participant extraction from transcript segments."""

import re
from collections.abc import Iterable

from organizational_memory.extraction.provenance import make_metadata
from organizational_memory.extraction.segmentation import Segment
from organizational_memory.models.participant import Participant

EXTRACTOR_NAME = "participant_extractor"

_ATTENDEE_PREFIX = re.compile(
    r"^\s*(?:attendees|participants|present|members)\s*:\s*(?P<names>.+)$",
    re.IGNORECASE,
)
_NAME_SPLIT = re.compile(r"\s*(?:,|;|/|\band\b|&)\s*", re.IGNORECASE)


def _attendee_names(text: str) -> list[str]:
    match = _ATTENDEE_PREFIX.match(text)
    if match is None:
        return []
    raw = _NAME_SPLIT.split(match.group("names"))
    return [name.strip() for name in raw if name.strip()]


def extract_participants(segments: Iterable[Segment]) -> list[Participant]:
    """Extract de-duplicated :class:`Participant` records from ``segments``."""
    participants: list[Participant] = []
    seen: set[str] = set()
    for segment in segments:
        candidates: list[tuple[str, str]] = []
        for name in _attendee_names(segment.text):
            candidates.append((name, "attendee_line"))
        if segment.speaker:
            candidates.append((segment.speaker, "speaker_turn"))
        for name, role in candidates:
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            participants.append(
                Participant(
                    name=name,
                    metadata=make_metadata(
                        extractor=EXTRACTOR_NAME,
                        matched_phrase=role,
                        segment=segment,
                    ),
                )
            )
    return participants
