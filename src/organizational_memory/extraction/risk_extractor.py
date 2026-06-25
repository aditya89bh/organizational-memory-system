"""Deterministic risk extraction from transcript segments."""

from collections.abc import Iterable

from organizational_memory.extraction.normalization import shorten
from organizational_memory.extraction.provenance import first_marker, make_metadata
from organizational_memory.extraction.segmentation import Segment
from organizational_memory.models.enums import Severity
from organizational_memory.models.risk import Risk

EXTRACTOR_NAME = "risk_extractor"

RISK_MARKERS: tuple[str, ...] = (
    "high risk",
    "risk:",
    "concern:",
    "possible issue",
    "might fail",
    "could delay",
)

_HIGH_SEVERITY_MARKERS = frozenset({"high risk", "might fail"})


def _severity_for(marker: str) -> Severity:
    return Severity.HIGH if marker in _HIGH_SEVERITY_MARKERS else Severity.MEDIUM


def extract_risks(segments: Iterable[Segment]) -> list[Risk]:
    """Extract :class:`Risk` records from ``segments``."""
    risks: list[Risk] = []
    for segment in segments:
        marker = first_marker(segment.text, RISK_MARKERS)
        if marker is None:
            continue
        risks.append(
            Risk(
                title=shorten(segment.text),
                description=segment.text,
                severity=_severity_for(marker),
                owner_id=segment.speaker,
                metadata=make_metadata(
                    extractor=EXTRACTOR_NAME,
                    matched_phrase=marker,
                    segment=segment,
                ),
            )
        )
    return risks
