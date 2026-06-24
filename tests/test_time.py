"""Tests for timestamp utilities."""

from datetime import UTC, datetime

import pytest

from organizational_memory.utils.time import (
    format_timestamp,
    parse_timestamp,
    utc_now,
)


def test_utc_now_is_timezone_aware() -> None:
    now = utc_now()
    assert now.tzinfo is not None
    assert now.utcoffset() == UTC.utcoffset(None)


def test_format_timestamp_uses_z_suffix() -> None:
    moment = datetime(2026, 6, 24, 9, 30, tzinfo=UTC)
    assert format_timestamp(moment) == "2026-06-24T09:30:00Z"


def test_format_timestamp_rejects_naive() -> None:
    with pytest.raises(ValueError, match="naive datetime"):
        format_timestamp(datetime(2026, 6, 24, 9, 30))


def test_parse_timestamp_accepts_z_suffix() -> None:
    parsed = parse_timestamp("2026-06-24T09:30:00Z")
    assert parsed == datetime(2026, 6, 24, 9, 30, tzinfo=UTC)


def test_parse_timestamp_assumes_utc_for_naive_input() -> None:
    parsed = parse_timestamp("2026-06-24T09:30:00")
    assert parsed.tzinfo is not None
    assert parsed.hour == 9


def test_roundtrip_is_stable() -> None:
    moment = utc_now()
    assert parse_timestamp(format_timestamp(moment)) == moment


def test_parse_timestamp_rejects_garbage() -> None:
    with pytest.raises(ValueError, match="Invalid ISO 8601"):
        parse_timestamp("not-a-timestamp")
