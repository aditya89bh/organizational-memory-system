"""Tests for the task extractor."""

from organizational_memory.extraction.segmentation import segment_text
from organizational_memory.extraction.task_extractor import extract_tasks

POSITIVE = """TODO: send the recap email
Task: update the roadmap
Alice: action: schedule the review
- [ ] write release notes
Bob: someone needs to test the build
"""

NEGATIVE = """Alice: great work everyone.
- a normal bullet point
Just a sentence.
"""


def test_extracts_tasks() -> None:
    tasks = extract_tasks(segment_text(POSITIVE))
    assert len(tasks) == 5
    assert all(t.title and t.description and t.owner_id for t in tasks)


def test_owner_from_speaker() -> None:
    tasks = extract_tasks(segment_text("Alice: needs to fix the bug"))
    assert tasks[0].owner_id == "Alice"


def test_owner_defaults_to_unattributed() -> None:
    tasks = extract_tasks(segment_text("TODO: clean up logs"))
    assert tasks[0].owner_id == "unattributed"


def test_checkbox_task() -> None:
    tasks = extract_tasks(segment_text("- [ ] write the docs"))
    assert tasks[0].metadata["matched_phrase"] == "[ ]"


def test_no_false_positives() -> None:
    assert extract_tasks(segment_text(NEGATIVE)) == []
