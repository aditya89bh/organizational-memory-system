"""Tests for the decision extractor."""

from organizational_memory.extraction.decision_extractor import extract_decisions
from organizational_memory.extraction.segmentation import segment_text
from organizational_memory.models.enums import DecisionStatus

POSITIVE = """Alice: We decided to ship on Friday.
Decision: adopt the new pricing model.
Bob: We will go with vendor A.
The board approved the budget.
"""

NEGATIVE = """Alice: What should we do about pricing?
- random discussion point
We talked about many options.
"""


def test_extracts_decisions() -> None:
    decisions = extract_decisions(segment_text(POSITIVE))
    assert len(decisions) == 4
    assert all(d.title and d.description for d in decisions)


def test_owner_from_speaker() -> None:
    decisions = extract_decisions(segment_text("Alice: We decided to ship."))
    assert decisions[0].owner_id == "Alice"


def test_accepted_status() -> None:
    decisions = extract_decisions(segment_text("The board approved the budget."))
    assert decisions[0].status is DecisionStatus.ACCEPTED


def test_proposed_status_for_plain_decision_label() -> None:
    decisions = extract_decisions(segment_text("Decision: revisit later."))
    assert decisions[0].status is DecisionStatus.PROPOSED


def test_no_false_positives() -> None:
    assert extract_decisions(segment_text(NEGATIVE)) == []


def test_provenance_metadata() -> None:
    decisions = extract_decisions(segment_text("Alice: We decided to ship."))
    meta = decisions[0].metadata
    assert meta["extractor"] == "decision_extractor"
    assert meta["matched_phrase"] == "we decided"
    assert meta["segment_id"] == "seg-1"
