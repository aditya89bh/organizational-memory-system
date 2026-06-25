"""Deterministic dependency extraction from transcript segments."""

from collections.abc import Iterable

from organizational_memory.extraction.normalization import shorten
from organizational_memory.extraction.provenance import first_marker, make_metadata
from organizational_memory.extraction.segmentation import Segment
from organizational_memory.models.dependency import Dependency

EXTRACTOR_NAME = "dependency_extractor"
_UNKNOWN_SOURCE = "unknown"

DEPENDENCY_MARKERS: tuple[str, ...] = (
    "cannot proceed until",
    "blocked by",
    "depends on",
    "waiting for",
    "requires",
)


def _target_after(text: str, marker: str) -> str:
    lowered = text.lower()
    position = lowered.find(marker)
    tail = text[position + len(marker) :].strip(" :-\u2013.")
    return shorten(tail) if tail else shorten(text)


def extract_dependencies(segments: Iterable[Segment]) -> list[Dependency]:
    """Extract :class:`Dependency` records from ``segments``."""
    dependencies: list[Dependency] = []
    for segment in segments:
        marker = first_marker(segment.text, DEPENDENCY_MARKERS)
        if marker is None:
            continue
        dependencies.append(
            Dependency(
                source_id=segment.speaker or _UNKNOWN_SOURCE,
                target_id=_target_after(segment.text, marker),
                dependency_type="depends_on",
                description=segment.text,
                metadata=make_metadata(
                    extractor=EXTRACTOR_NAME,
                    matched_phrase=marker,
                    segment=segment,
                ),
            )
        )
    return dependencies
