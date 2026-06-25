"""Tests for the extraction pipeline."""

from organizational_memory.extraction.pipeline import (
    ExtractionResult,
    run_extraction,
)
from organizational_memory.ingestion.transcript_loader import Transcript

TRANSCRIPT = """# Weekly Sync

Attendees: Alice, Bob

Alice: We decided to ship on Friday.
Bob: I will own the release notes.
TODO: update the changelog
Alice: What is the rollback plan?
Bob: The launch is blocked by the security review.
Risk: the vendor might miss the deadline.
Topic: Pricing
"""


def test_pipeline_returns_result() -> None:
    result = run_extraction(TRANSCRIPT)
    assert isinstance(result, ExtractionResult)


def test_pipeline_accepts_transcript_object() -> None:
    result = run_extraction(Transcript(text=TRANSCRIPT))
    assert result.decisions


def test_pipeline_populates_categories() -> None:
    result = run_extraction(TRANSCRIPT)
    assert [p.name for p in result.participants][:2] == ["Alice", "Bob"]
    assert len(result.decisions) == 1
    assert len(result.commitments) == 1
    assert len(result.tasks) == 1
    assert len(result.open_loops) == 1
    assert len(result.dependencies) == 1
    assert len(result.risks) == 1
    assert result.action_items
    assert any(t.title == "Pricing" for t in result.topics)


def test_pipeline_segments_present() -> None:
    result = run_extraction(TRANSCRIPT)
    assert result.segments
    assert result.speaker_turns
