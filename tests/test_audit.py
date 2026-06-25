"""Tests for extraction audit traces."""

from organizational_memory.extraction.audit import build_trace, build_traces
from organizational_memory.extraction.decision_extractor import extract_decisions
from organizational_memory.extraction.pipeline import run_extraction
from organizational_memory.extraction.segmentation import segment_text


def test_build_trace_fields() -> None:
    decision = extract_decisions(segment_text("Alice: We decided to ship."))[0]
    decision.metadata["confidence"] = "0.85"
    trace = build_trace(decision)
    assert trace.record_id == decision.id
    assert trace.extractor == "decision_extractor"
    assert trace.matched_phrase == "we decided"
    assert trace.source_line == "We decided to ship."
    assert trace.segment_id == "seg-1"
    assert trace.confidence == 0.85


def test_build_traces_count() -> None:
    decisions = extract_decisions(
        segment_text("We decided A.\nWe decided B.")
    )
    assert len(build_traces(decisions)) == 2


def test_pipeline_produces_traces() -> None:
    result = run_extraction("Alice: We decided to ship on Friday.")
    assert result.traces
    extractors = {trace.extractor for trace in result.traces}
    assert "decision_extractor" in extractors
    assert all(0.0 <= trace.confidence <= 1.0 for trace in result.traces)


def test_invalid_confidence_defaults_to_zero() -> None:
    decision = extract_decisions(segment_text("We decided to ship."))[0]
    decision.metadata["confidence"] = "not-a-number"
    assert build_trace(decision).confidence == 0.0
