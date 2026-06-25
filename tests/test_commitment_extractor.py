"""Tests for the commitment extractor."""

from organizational_memory.extraction.commitment_extractor import (
    extract_commitments,
)
from organizational_memory.extraction.segmentation import segment_text

POSITIVE = """Alice: I will prepare the proposal.
Bob: I'll review the API design.
Carol: I commit to delivering the report.
We will migrate the database.
"""

NEGATIVE = """Alice: That sounds reasonable.
- a plain note
The weather is nice.
"""


def test_extracts_commitments() -> None:
    commitments = extract_commitments(segment_text(POSITIVE))
    assert len(commitments) == 4
    assert all(c.owner_id and c.description for c in commitments)


def test_owner_from_speaker() -> None:
    commitments = extract_commitments(segment_text("Alice: I will do it."))
    assert commitments[0].owner_id == "Alice"


def test_owner_defaults_to_unattributed() -> None:
    commitments = extract_commitments(segment_text("We will migrate later."))
    assert commitments[0].owner_id == "unattributed"


def test_no_false_positives() -> None:
    assert extract_commitments(segment_text(NEGATIVE)) == []


def test_provenance_metadata() -> None:
    commitments = extract_commitments(segment_text("Alice: I will do it."))
    meta = commitments[0].metadata
    assert meta["extractor"] == "commitment_extractor"
    assert meta["matched_phrase"] == "i will"
