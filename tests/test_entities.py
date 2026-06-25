"""Tests for entity extraction."""

from organizational_memory.extraction.entities import (
    extract_capitalized_phrases,
    extract_dates,
    extract_entities,
    extract_persons,
)
from organizational_memory.extraction.segmentation import segment_text


def test_extract_persons_unique_and_ordered() -> None:
    text = "Alice: hi\nBob: hello\nAlice: again"
    assert extract_persons(segment_text(text)) == ["Alice", "Bob"]


def test_extract_dates() -> None:
    text = "Ship by Friday, review on 2026-07-01, plan next week and in Q3."
    dates = extract_dates(text)
    assert "Friday" in dates
    assert "2026-07-01" in dates
    assert "next week" in dates
    assert "Q3" in dates


def test_extract_dates_month_day() -> None:
    assert "January 5" in extract_dates("The deadline is January 5.")


def test_extract_capitalized_phrases() -> None:
    phrases = extract_capitalized_phrases("We will launch Project Phoenix soon.")
    assert "Project Phoenix" in phrases


def test_extract_entities_bundle() -> None:
    text = "Alice: Project Phoenix ships Friday."
    entities = extract_entities(segment_text(text), text)
    assert entities.persons == ["Alice"]
    assert "Friday" in entities.dates
    assert "Project Phoenix" in entities.topics
