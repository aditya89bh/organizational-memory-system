"""Tests for the markdown loader."""

from pathlib import Path

from organizational_memory.ingestion import (
    TranscriptFormat,
    classify_markdown_lines,
    heading_texts,
    load_markdown_from_file,
    load_markdown_from_string,
)

SAMPLE = """# Sprint Planning

## Decisions
- We decided to ship on Friday
- Alice: I will own the API

Some closing notes.
"""


def test_load_markdown_from_string() -> None:
    transcript = load_markdown_from_string(SAMPLE, source="notes.md")
    assert transcript.content_format is TranscriptFormat.MARKDOWN
    assert transcript.source == "notes.md"
    assert transcript.text == SAMPLE


def test_classify_lines_detects_headings_and_bullets() -> None:
    lines = classify_markdown_lines(SAMPLE)
    headings = [line for line in lines if line.is_heading]
    bullets = [line for line in lines if line.is_bullet]
    assert len(headings) == 2
    assert len(bullets) == 2
    assert all(not line.is_heading or not line.is_bullet for line in lines)


def test_heading_texts() -> None:
    assert heading_texts(SAMPLE) == ["Sprint Planning", "Decisions"]


def test_blank_lines_are_skipped() -> None:
    assert all(line.text.strip() for line in classify_markdown_lines(SAMPLE))


def test_load_markdown_from_file(tmp_path: Path) -> None:
    path = tmp_path / "notes.md"
    path.write_text(SAMPLE, encoding="utf-8")
    transcript = load_markdown_from_file(path)
    assert transcript.content_format is TranscriptFormat.MARKDOWN
    assert transcript.source == str(path)
