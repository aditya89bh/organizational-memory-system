"""Tests for the risk extractor."""

from organizational_memory.extraction.risk_extractor import extract_risks
from organizational_memory.extraction.segmentation import segment_text
from organizational_memory.models.enums import Severity

POSITIVE = """Risk: the vendor may miss the deadline.
Alice: my concern: scope creep.
There is a possible issue with latency.
The integration might fail under load.
This could delay the launch.
This is a high risk area.
"""

NEGATIVE = """Alice: everything looks solid.
- a normal note
We are confident.
"""


def test_extracts_risks() -> None:
    risks = extract_risks(segment_text(POSITIVE))
    assert len(risks) == 6
    assert all(r.title and r.description for r in risks)


def test_high_severity() -> None:
    risks = extract_risks(segment_text("This is a high risk area."))
    assert risks[0].severity is Severity.HIGH


def test_medium_severity_default() -> None:
    risks = extract_risks(segment_text("Risk: minor cosmetic bug."))
    assert risks[0].severity is Severity.MEDIUM


def test_owner_from_speaker() -> None:
    risks = extract_risks(segment_text("Alice: concern: timeline is tight."))
    assert risks[0].owner_id == "Alice"


def test_no_false_positives() -> None:
    assert extract_risks(segment_text(NEGATIVE)) == []
