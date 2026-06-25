"""Deterministic commitment extraction from transcript segments."""

from collections.abc import Iterable

from organizational_memory.extraction.provenance import (
    UNATTRIBUTED_OWNER,
    first_marker,
    make_metadata,
)
from organizational_memory.extraction.segmentation import Segment
from organizational_memory.models.commitment import Commitment

EXTRACTOR_NAME = "commitment_extractor"

COMMITMENT_MARKERS: tuple[str, ...] = (
    "i commit to",
    "i will own",
    "i will",
    "i'll",
    "i\u2019ll",
    "i can take",
    "we will",
)


def extract_commitments(segments: Iterable[Segment]) -> list[Commitment]:
    """Extract :class:`Commitment` records from ``segments``."""
    commitments: list[Commitment] = []
    for segment in segments:
        marker = first_marker(segment.text, COMMITMENT_MARKERS)
        if marker is None:
            continue
        owner = segment.speaker or UNATTRIBUTED_OWNER
        commitments.append(
            Commitment(
                owner_id=owner,
                description=segment.text,
                metadata=make_metadata(
                    extractor=EXTRACTOR_NAME,
                    matched_phrase=marker,
                    segment=segment,
                ),
            )
        )
    return commitments
