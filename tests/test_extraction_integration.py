"""Integration tests for the end-to-end extraction pipeline."""

from organizational_memory.extraction.config import ExtractionConfig
from organizational_memory.extraction.pipeline import run_extraction
from organizational_memory.ingestion.markdown_loader import load_markdown_from_string

FULL_MEETING = """# Product Sync

Attendees: Aditya, Priya, Rahul

[10:00] Aditya: We decided to launch the beta on Friday.
[10:02] Priya: I will prepare the onboarding docs.
[10:04] Rahul: The launch is blocked by the security review.
[10:05] Aditya: What is our rollback plan?
Risk: the vendor might miss the deadline.
TODO: finalize the pricing page.
Topic: Beta launch
"""

MARKDOWN_NOTES = """# Sprint Planning

## Decisions
- We decided to adopt the new CI pipeline.

## Commitments
- Maria: I will own the migration.

## Open Questions
- Who signs off on the release?
"""


def test_full_meeting_extracts_all_categories() -> None:
    result = run_extraction(FULL_MEETING)
    assert len(result.decisions) == 1
    assert len(result.commitments) == 1
    assert len(result.open_loops) == 1
    assert len(result.dependencies) == 1
    assert len(result.risks) == 1
    assert len(result.tasks) == 1
    assert {p.name for p in result.participants} >= {"Aditya", "Priya", "Rahul"}


def test_speaker_attribution_flows_to_records() -> None:
    result = run_extraction(FULL_MEETING)
    assert result.decisions[0].owner_id == "Aditya"
    assert result.commitments[0].owner_id == "Priya"
    assert result.dependencies[0].source_id == "Rahul"


def test_markdown_notes_extraction() -> None:
    transcript = load_markdown_from_string(MARKDOWN_NOTES)
    result = run_extraction(transcript)
    assert result.decisions
    assert result.commitments
    assert result.open_loops
    assert any(t.title == "Decisions" for t in result.topics)


def test_confidence_filtering_reduces_results() -> None:
    unfiltered = run_extraction(FULL_MEETING)
    filtered = run_extraction(FULL_MEETING, ExtractionConfig(min_confidence=0.85))
    total_unfiltered = len(unfiltered.decisions) + len(unfiltered.tasks)
    total_filtered = len(filtered.decisions) + len(filtered.tasks)
    assert total_filtered <= total_unfiltered


def test_traces_cover_all_records() -> None:
    result = run_extraction(FULL_MEETING)
    record_total = (
        len(result.participants)
        + len(result.decisions)
        + len(result.commitments)
        + len(result.tasks)
        + len(result.open_loops)
        + len(result.dependencies)
        + len(result.risks)
        + len(result.action_items)
        + len(result.topics)
    )
    assert len(result.traces) == record_total
