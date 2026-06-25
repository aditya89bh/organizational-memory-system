"""Tests for extraction configuration."""

import pytest

from organizational_memory.extraction.config import (
    ALL_EXTRACTORS,
    ExtractionConfig,
    default_config,
)
from organizational_memory.extraction.errors import (
    EmptyTranscriptError,
    InvalidExtractionConfigError,
)
from organizational_memory.extraction.pipeline import run_extraction

TRANSCRIPT = """Alice: We decided to ship on Friday.
Bob: I will own the release notes.
Carol: maybe we should reconsider the timeline.
"""


def test_default_config() -> None:
    config = default_config()
    assert config.min_confidence == 0.0
    assert config.enabled_extractors == ALL_EXTRACTORS
    assert config.filter_duplicates is True


def test_invalid_min_confidence() -> None:
    with pytest.raises(InvalidExtractionConfigError):
        ExtractionConfig(min_confidence=1.5)


def test_unknown_extractor() -> None:
    with pytest.raises(InvalidExtractionConfigError):
        ExtractionConfig(enabled_extractors=frozenset({"made_up_extractor"}))


def test_disabled_extractor_yields_empty() -> None:
    config = ExtractionConfig(enabled_extractors=frozenset({"commitment_extractor"}))
    result = run_extraction(TRANSCRIPT, config)
    assert result.decisions == []
    assert result.commitments


def test_min_confidence_filters_records() -> None:
    high = ExtractionConfig(min_confidence=0.99)
    result = run_extraction(TRANSCRIPT, high)
    assert result.decisions == []


def test_parse_dates_toggle() -> None:
    text = "Alice: We decided to ship on Friday."
    with_dates = run_extraction(text, ExtractionConfig(parse_dates=True))
    without_dates = run_extraction(text, ExtractionConfig(parse_dates=False))
    assert with_dates.entities.dates
    assert without_dates.entities.dates == []


def test_strict_mode_raises_when_empty() -> None:
    with pytest.raises(EmptyTranscriptError):
        run_extraction("nothing notable here", ExtractionConfig(strict=True))
