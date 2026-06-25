"""Tests for the transcript loader."""

from pathlib import Path

from organizational_memory.ingestion import (
    Transcript,
    TranscriptFormat,
    load_transcript_from_file,
    load_transcript_from_string,
)


def test_load_from_string() -> None:
    transcript = load_transcript_from_string("Alice: hello\nBob: hi")
    assert isinstance(transcript, Transcript)
    assert transcript.content_format is TranscriptFormat.TEXT
    assert transcript.lines == ["Alice: hello", "Bob: hi"]
    assert transcript.source is None
    assert not transcript.is_empty


def test_empty_transcript_flag() -> None:
    assert load_transcript_from_string("   \n  ").is_empty


def test_load_from_file(tmp_path: Path) -> None:
    file_path = tmp_path / "meeting.txt"
    file_path.write_text("Alice: hello\n", encoding="utf-8")
    transcript = load_transcript_from_file(file_path)
    assert transcript.text == "Alice: hello\n"
    assert transcript.source == str(file_path)
    assert transcript.lines == ["Alice: hello"]
