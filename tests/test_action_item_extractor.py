"""Tests for the action item extractor."""

from organizational_memory.extraction.action_item_extractor import (
    extract_action_items,
)
from organizational_memory.extraction.segmentation import segment_text

POSITIVE = """TODO: send the recap
Alice: I will own the rollout
- [ ] write the docs
Bob: needs to test the build
"""

NEGATIVE = """Alice: nice work.
- a normal note
All done.
"""


def test_extracts_action_items() -> None:
    items = extract_action_items(segment_text(POSITIVE))
    assert len(items) == 4
    assert all(item.description for item in items)


def test_owner_from_speaker() -> None:
    items = extract_action_items(segment_text("Alice: I will own the rollout"))
    assert items[0].owner_id == "Alice"


def test_deduplicates_identical_lines() -> None:
    items = extract_action_items(segment_text("TODO: ship it\nTODO: ship it"))
    assert len(items) == 1


def test_no_false_positives() -> None:
    assert extract_action_items(segment_text(NEGATIVE)) == []
