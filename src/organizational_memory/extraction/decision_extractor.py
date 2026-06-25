"""Deterministic decision extraction from transcript segments."""

from collections.abc import Iterable

from organizational_memory.extraction.normalization import shorten
from organizational_memory.extraction.provenance import first_marker, make_metadata
from organizational_memory.extraction.segmentation import Segment
from organizational_memory.models.decision import Decision
from organizational_memory.models.enums import DecisionStatus

EXTRACTOR_NAME = "decision_extractor"

DECISION_MARKERS: tuple[str, ...] = (
    "final decision",
    "we decided",
    "decision:",
    "agreed to",
    "we will go with",
    "approved",
)

_ACCEPTED_MARKERS = frozenset(
    {
        "final decision",
        "we decided",
        "agreed to",
        "we will go with",
        "approved",
    }
)


def _status_for(marker: str) -> DecisionStatus:
    return (
        DecisionStatus.ACCEPTED
        if marker in _ACCEPTED_MARKERS
        else DecisionStatus.PROPOSED
    )


def extract_decisions(segments: Iterable[Segment]) -> list[Decision]:
    """Extract :class:`Decision` records from ``segments``."""
    decisions: list[Decision] = []
    for segment in segments:
        marker = first_marker(segment.text, DECISION_MARKERS)
        if marker is None:
            continue
        decisions.append(
            Decision(
                title=shorten(segment.text),
                description=segment.text,
                owner_id=segment.speaker,
                status=_status_for(marker),
                metadata=make_metadata(
                    extractor=EXTRACTOR_NAME,
                    matched_phrase=marker,
                    segment=segment,
                ),
            )
        )
    return decisions
