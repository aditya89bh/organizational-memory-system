"""Audit traces linking extracted records back to their source."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from organizational_memory.extraction.provenance import (
    CONFIDENCE_KEY,
    EXTRACTOR_KEY,
    MATCHED_PHRASE_KEY,
    SEGMENT_ID_KEY,
    SOURCE_LINE_KEY,
)


class TraceableRecord(Protocol):
    """Structural type for records that can be traced to their source."""

    id: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class ExtractionTrace:
    """A typed view of where an extracted record came from.

    Attributes:
        record_id: Identifier of the extracted record.
        extractor: Name of the extractor that produced the record.
        matched_phrase: The deterministic phrase that triggered extraction.
        source_line: The source segment text the record was derived from.
        segment_id: Identifier of the source segment.
        confidence: Deterministic confidence score in ``[0, 1]``.
    """

    record_id: str
    extractor: str
    matched_phrase: str
    source_line: str
    segment_id: str
    confidence: float


def _parse_confidence(raw: str) -> float:
    try:
        return float(raw)
    except ValueError:
        return 0.0


def build_trace(record: TraceableRecord) -> ExtractionTrace:
    """Build an :class:`ExtractionTrace` from a record's provenance metadata."""
    metadata = record.metadata
    return ExtractionTrace(
        record_id=record.id,
        extractor=metadata.get(EXTRACTOR_KEY, ""),
        matched_phrase=metadata.get(MATCHED_PHRASE_KEY, ""),
        source_line=metadata.get(SOURCE_LINE_KEY, ""),
        segment_id=metadata.get(SEGMENT_ID_KEY, ""),
        confidence=_parse_confidence(metadata.get(CONFIDENCE_KEY, "0")),
    )


def build_traces(records: Iterable[TraceableRecord]) -> list[ExtractionTrace]:
    """Build audit traces for every record in ``records``."""
    return [build_trace(record) for record in records]
