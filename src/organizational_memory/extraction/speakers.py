"""Detect speaker turns in transcript lines.

Recognizes lines such as::

    Aditya: We should ship this by Friday.
    Priya - I will prepare the proposal.
    [10:30] Rahul: The API is blocked.
"""

import re
from dataclasses import dataclass

_SPEAKER_LINE = re.compile(
    r"""
    ^\s*
    (?:[\[(]?(?P<timestamp>\d{1,2}:\d{2}(?::\d{2})?\s*(?:[AaPp][Mm])?)[\])]?\s+)?
    (?P<speaker>[A-Z][\w.'\u2019-]*(?:\s+[A-Z][\w.'\u2019-]*){0,3})
    \s*[:\u2013-]\s+
    (?P<text>\S.*)
    $
    """,
    re.VERBOSE,
)


_RESERVED_LABELS = frozenset(
    {
        "action",
        "actions",
        "agenda",
        "attendees",
        "blocker",
        "blockers",
        "concern",
        "concerns",
        "decision",
        "decisions",
        "dependencies",
        "dependency",
        "next",
        "note",
        "notes",
        "open",
        "participants",
        "recap",
        "risk",
        "risks",
        "status",
        "summary",
        "task",
        "tasks",
        "tbd",
        "todo",
        "topic",
        "topics",
        "unresolved",
        "update",
        "updates",
    }
)


@dataclass(frozen=True)
class SpeakerMatch:
    """A speaker detection result for a single line of text."""

    speaker: str
    text: str
    timestamp: str | None


@dataclass(frozen=True)
class SpeakerTurn:
    """A speaker turn anchored to its source line number."""

    speaker: str
    text: str
    line_number: int
    timestamp: str | None = None


def match_speaker(line: str) -> SpeakerMatch | None:
    """Return a :class:`SpeakerMatch` if ``line`` looks like a speaker turn."""
    match = _SPEAKER_LINE.match(line)
    if match is None:
        return None
    speaker = match.group("speaker").strip()
    if " " not in speaker and speaker.lower() in _RESERVED_LABELS:
        return None
    timestamp = match.group("timestamp")
    return SpeakerMatch(
        speaker=speaker,
        text=match.group("text").strip(),
        timestamp=timestamp.strip() if timestamp else None,
    )


def parse_speaker_turns(text: str) -> list[SpeakerTurn]:
    """Parse all speaker turns from ``text``, preserving line numbers."""
    turns: list[SpeakerTurn] = []
    for index, line in enumerate(text.splitlines(), start=1):
        matched = match_speaker(line)
        if matched is None:
            continue
        turns.append(
            SpeakerTurn(
                speaker=matched.speaker,
                text=matched.text,
                line_number=index,
                timestamp=matched.timestamp,
            )
        )
    return turns
