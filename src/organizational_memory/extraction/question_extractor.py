"""Deterministic open-question extraction from transcript segments."""

from collections.abc import Iterable

from organizational_memory.extraction.provenance import first_marker, make_metadata
from organizational_memory.extraction.segmentation import Segment
from organizational_memory.models.open_loop import OpenLoop

EXTRACTOR_NAME = "question_extractor"

QUESTION_MARKERS: tuple[str, ...] = (
    "open question:",
    "unresolved:",
    "need to clarify",
    "blocked on answer",
    "tbd",
)


def _matched_phrase(text: str) -> str | None:
    marker = first_marker(text, QUESTION_MARKERS)
    if marker is not None:
        return marker
    if text.rstrip().endswith("?"):
        return "?"
    return None


def extract_questions(segments: Iterable[Segment]) -> list[OpenLoop]:
    """Extract :class:`OpenLoop` records from ``segments``."""
    open_loops: list[OpenLoop] = []
    for segment in segments:
        marker = _matched_phrase(segment.text)
        if marker is None:
            continue
        open_loops.append(
            OpenLoop(
                question=segment.text,
                owner_id=segment.speaker,
                metadata=make_metadata(
                    extractor=EXTRACTOR_NAME,
                    matched_phrase=marker,
                    segment=segment,
                ),
            )
        )
    return open_loops
