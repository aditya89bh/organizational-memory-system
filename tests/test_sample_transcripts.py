"""Tests that load the bundled example transcripts."""

from pathlib import Path

import pytest

from organizational_memory.extraction.pipeline import run_extraction
from organizational_memory.ingestion.markdown_loader import load_markdown_from_file
from organizational_memory.ingestion.transcript_loader import (
    load_transcript_from_file,
)

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "transcripts"


def test_example_files_exist() -> None:
    names = {path.name for path in EXAMPLES_DIR.iterdir()}
    assert {
        "startup_product_meeting.txt",
        "sprint_planning_meeting.md",
        "board_review_meeting.txt",
    } <= names


@pytest.mark.parametrize(
    "filename",
    ["startup_product_meeting.txt", "board_review_meeting.txt"],
)
def test_text_samples_extract_records(filename: str) -> None:
    transcript = load_transcript_from_file(EXAMPLES_DIR / filename)
    result = run_extraction(transcript)
    assert result.decisions
    assert result.commitments
    assert result.open_loops
    assert result.risks


def test_markdown_sample_extracts_records() -> None:
    transcript = load_markdown_from_file(EXAMPLES_DIR / "sprint_planning_meeting.md")
    result = run_extraction(transcript)
    assert len(result.decisions) >= 2
    assert result.commitments
    assert result.tasks
    assert result.dependencies
    assert result.open_loops
