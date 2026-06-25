"""Tests for the topic extractor."""

from organizational_memory.extraction.segmentation import segment_text
from organizational_memory.extraction.topic_extractor import extract_topics

SAMPLE = """# Sprint Planning

## Roadmap

Topic: Pricing strategy
Alice: let's discuss.
"""


def test_extracts_headings_and_topic_lines() -> None:
    topics = extract_topics(segment_text(SAMPLE))
    titles = [t.title for t in topics]
    assert titles == ["Sprint Planning", "Roadmap", "Pricing strategy"]


def test_topic_line_provenance() -> None:
    topics = extract_topics(segment_text("Topic: Budget review"))
    assert topics[0].metadata["matched_phrase"] == "topic:"


def test_heading_provenance() -> None:
    topics = extract_topics(segment_text("# Kickoff"))
    assert topics[0].metadata["matched_phrase"] == "heading"


def test_deduplicates_titles() -> None:
    topics = extract_topics(segment_text("# Roadmap\nTopic: roadmap"))
    assert len(topics) == 1


def test_no_topics() -> None:
    assert extract_topics(segment_text("Alice: just chatting\nplain text")) == []
