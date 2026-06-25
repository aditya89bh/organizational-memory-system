"""Shared helpers for deterministic marker matching and provenance metadata.

Every extractor records where a record came from by writing a small set of
metadata keys onto the produced record. Later stages (confidence scoring and
audit traces) read these keys back into typed structures.
"""

from organizational_memory.extraction.segmentation import Segment

UNATTRIBUTED_OWNER = "unattributed"

EXTRACTOR_KEY = "extractor"
MATCHED_PHRASE_KEY = "matched_phrase"
SOURCE_LINE_KEY = "source_line"
SEGMENT_ID_KEY = "segment_id"
CONFIDENCE_KEY = "confidence"


def first_marker(text: str, markers: tuple[str, ...]) -> str | None:
    """Return the first marker (in order) found in ``text``, case-insensitive."""
    lowered = text.lower()
    for marker in markers:
        if marker in lowered:
            return marker
    return None


def make_metadata(
    *,
    extractor: str,
    matched_phrase: str,
    segment: Segment,
) -> dict[str, str]:
    """Build the provenance metadata dictionary for an extracted record."""
    return {
        EXTRACTOR_KEY: extractor,
        MATCHED_PHRASE_KEY: matched_phrase,
        SOURCE_LINE_KEY: segment.text,
        SEGMENT_ID_KEY: segment.id,
    }
