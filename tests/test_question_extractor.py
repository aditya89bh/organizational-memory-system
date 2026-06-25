"""Tests for the question extractor."""

from organizational_memory.extraction.question_extractor import extract_questions
from organizational_memory.extraction.segmentation import segment_text

POSITIVE = """Alice: What is the launch date?
Open question: who owns billing?
Unresolved: pricing tiers
We need to clarify the SLA terms.
Bob: the vendor name is TBD
"""

NEGATIVE = """Alice: We shipped the feature.
- a normal note
All clear.
"""


def test_extracts_open_loops() -> None:
    loops = extract_questions(segment_text(POSITIVE))
    assert len(loops) == 5
    assert all(loop.question for loop in loops)


def test_question_mark_detection() -> None:
    loops = extract_questions(segment_text("Alice: Are we ready?"))
    assert loops[0].metadata["matched_phrase"] == "?"
    assert loops[0].owner_id == "Alice"


def test_marker_detection() -> None:
    loops = extract_questions(segment_text("Unresolved: the budget"))
    assert loops[0].metadata["matched_phrase"] == "unresolved:"


def test_no_false_positives() -> None:
    assert extract_questions(segment_text(NEGATIVE)) == []
