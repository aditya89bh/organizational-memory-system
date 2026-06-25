"""Tests for the recall query parser."""

import pytest

from organizational_memory.recall.query_parser import parse_query


def test_parse_owner_and_status() -> None:
    parsed = parse_query("owner:aditya status:open")
    assert parsed.owner == "aditya"
    assert parsed.status == "open"
    assert parsed.text == ""


def test_parse_type_and_free_text() -> None:
    parsed = parse_query("type:decision kubernetes rollout")
    assert parsed.record_type == "Decision"
    assert parsed.text == "kubernetes rollout"


def test_parse_date_window() -> None:
    parsed = parse_query("after:2026-01-01 before:2026-02-01")
    assert parsed.after is not None
    assert parsed.before is not None
    assert parsed.after.year == 2026
    assert parsed.before.month == 2


def test_parse_priority_and_severity() -> None:
    parsed = parse_query("priority:high severity:critical")
    assert parsed.priority == "high"
    assert parsed.severity == "critical"


def test_parse_meeting_filter() -> None:
    parsed = parse_query("meeting:m123 pricing")
    assert parsed.source_meeting_id == "m123"
    assert parsed.text == "pricing"


def test_unknown_key_is_free_text() -> None:
    parsed = parse_query("foo:bar baz")
    assert parsed.text == "foo:bar baz"


def test_invalid_date_raises() -> None:
    with pytest.raises(ValueError, match="invalid date"):
        parse_query("after:not-a-date")


def test_type_alias_passthrough_for_unknown() -> None:
    parsed = parse_query("type:Widget")
    assert parsed.record_type == "Widget"
