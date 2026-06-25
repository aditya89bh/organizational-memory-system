"""Tests for extraction error handling."""

from typing import cast

import pytest

from organizational_memory.exceptions import OrganizationalMemoryError
from organizational_memory.extraction.errors import (
    EmptyTranscriptError,
    UnreadableSourceError,
    UnsupportedInputError,
)
from organizational_memory.extraction.pipeline import run_extraction
from organizational_memory.ingestion.transcript_loader import (
    Transcript,
    load_transcript_from_file,
)


def test_errors_subclass_base() -> None:
    assert issubclass(EmptyTranscriptError, OrganizationalMemoryError)


def test_empty_transcript_raises() -> None:
    with pytest.raises(EmptyTranscriptError):
        run_extraction("   \n\n  ")


def test_unsupported_input_raises() -> None:
    with pytest.raises(UnsupportedInputError):
        run_extraction(cast("Transcript", 123))


def test_unreadable_file_raises(tmp_path: object) -> None:
    missing = f"{tmp_path}/does-not-exist.txt"
    with pytest.raises(UnreadableSourceError):
        load_transcript_from_file(missing)
