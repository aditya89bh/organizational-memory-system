"""Tests for the dependency extractor."""

from organizational_memory.extraction.dependency_extractor import (
    extract_dependencies,
)
from organizational_memory.extraction.segmentation import segment_text

POSITIVE = """Alice: The launch is blocked by the security review.
Billing depends on the payments API.
We are waiting for legal sign-off.
The rollout cannot proceed until QA passes.
This requires a database migration.
"""

NEGATIVE = """Alice: Everything is on track.
- a normal note
We finished early.
"""


def test_extracts_dependencies() -> None:
    deps = extract_dependencies(segment_text(POSITIVE))
    assert len(deps) == 5
    assert all(d.source_id and d.target_id for d in deps)


def test_source_from_speaker() -> None:
    deps = extract_dependencies(
        segment_text("Alice: The launch is blocked by the security review.")
    )
    assert deps[0].source_id == "Alice"
    assert "security review" in deps[0].target_id


def test_source_defaults_to_unknown() -> None:
    deps = extract_dependencies(segment_text("Billing depends on the payments API."))
    assert deps[0].source_id == "unknown"
    assert deps[0].target_id == "the payments API"


def test_no_false_positives() -> None:
    assert extract_dependencies(segment_text(NEGATIVE)) == []
