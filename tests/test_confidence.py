"""Tests for confidence scoring."""

from organizational_memory.extraction.confidence import (
    marker_strength,
    score,
    score_record,
)
from organizational_memory.extraction.decision_extractor import extract_decisions
from organizational_memory.extraction.pipeline import run_extraction
from organizational_memory.extraction.segmentation import segment_text


def test_marker_strength_levels() -> None:
    assert marker_strength("decision:") == 0.9
    assert marker_strength("we decided") == 0.8
    assert marker_strength("heading") == 0.7
    assert marker_strength("?") == 0.55
    assert marker_strength("we will") == 0.6


def test_score_bounds_and_signals() -> None:
    high = score(
        strength=0.9, has_owner=True, has_due=True, line_length=40, ambiguous=False
    )
    low = score(
        strength=0.6, has_owner=False, has_due=False, line_length=4, ambiguous=True
    )
    assert 0.0 <= low < high <= 1.0


def test_ambiguous_penalty() -> None:
    decisions = extract_decisions(
        segment_text("Alice: We decided maybe to ship later.")
    )
    confident = extract_decisions(segment_text("Alice: We decided to ship Friday."))
    assert score_record(decisions[0]) < score_record(confident[0])


def test_pipeline_annotates_confidence() -> None:
    result = run_extraction("Alice: We decided to ship on Friday.")
    confidence = result.decisions[0].metadata["confidence"]
    assert 0.0 <= float(confidence) <= 1.0
