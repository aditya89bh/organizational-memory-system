"""Deterministic confidence scoring for extracted records.

Scores are computed purely from the provenance metadata recorded by each
extractor plus a few fields on the record itself, so the same input always
yields the same score.
"""

from collections.abc import Iterable
from typing import Protocol

from organizational_memory.extraction.provenance import (
    CONFIDENCE_KEY,
    MATCHED_PHRASE_KEY,
    SOURCE_LINE_KEY,
    UNATTRIBUTED_OWNER,
)


class MetadataRecord(Protocol):
    """Structural type for extracted records carrying provenance metadata."""

    metadata: dict[str, str]

_STRONG_MARKERS = frozenset(
    {
        "we decided",
        "approved",
        "agreed to",
        "final decision",
        "we will go with",
        "blocked by",
        "depends on",
        "cannot proceed until",
        "i commit to",
        "i will own",
    }
)
_STRUCTURAL_MARKERS = frozenset({"heading", "speaker_turn", "attendee_line"})
_AMBIGUOUS_WORDS = (
    "maybe",
    "perhaps",
    "possibly",
    "not sure",
    "tentative",
    "i think",
)
_PLACEHOLDER_OWNERS = frozenset({UNATTRIBUTED_OWNER, "unknown", ""})

_MIN_QUALITY_LEN = 12
_MAX_QUALITY_LEN = 240


def marker_strength(phrase: str) -> float:
    """Return the base confidence contributed by ``phrase``."""
    if phrase.endswith(":"):
        return 0.9
    if phrase in _STRONG_MARKERS:
        return 0.8
    if phrase in _STRUCTURAL_MARKERS:
        return 0.7
    if phrase == "?":
        return 0.55
    return 0.6


def score(
    *,
    strength: float,
    has_owner: bool,
    has_due: bool,
    line_length: int,
    ambiguous: bool,
) -> float:
    """Combine deterministic signals into a confidence score in ``[0, 1]``."""
    value = strength
    if has_owner:
        value += 0.05
    if has_due:
        value += 0.05
    if _MIN_QUALITY_LEN <= line_length <= _MAX_QUALITY_LEN:
        value += 0.05
    else:
        value -= 0.05
    if ambiguous:
        value -= 0.15
    return round(min(1.0, max(0.0, value)), 3)


def score_record(record: MetadataRecord) -> float:
    """Compute the confidence score for a single extracted ``record``."""
    metadata = record.metadata
    phrase = metadata.get(MATCHED_PHRASE_KEY, "")
    line = metadata.get(SOURCE_LINE_KEY, "")
    owner = getattr(record, "owner_id", None)
    has_owner = bool(owner) and str(owner).lower() not in _PLACEHOLDER_OWNERS
    has_due = getattr(record, "due_at", None) is not None
    ambiguous = any(word in line.lower() for word in _AMBIGUOUS_WORDS)
    return score(
        strength=marker_strength(phrase),
        has_owner=has_owner,
        has_due=has_due,
        line_length=len(line),
        ambiguous=ambiguous,
    )


def annotate_confidence(records: Iterable[MetadataRecord]) -> None:
    """Write the confidence score into each record's provenance metadata."""
    for record in records:
        record.metadata[CONFIDENCE_KEY] = f"{score_record(record):.3f}"
