"""Tests for local error reporting."""

import json

from organizational_memory.observability.error_reporting import (
    build_error_report,
    summarize_traceback,
)
from organizational_memory.utils.time import parse_timestamp

FIXED = parse_timestamp("2026-03-01T00:00:00Z")


def _raise() -> None:
    raise ValueError("boom")


def _caught() -> Exception:
    try:
        _raise()
    except ValueError as error:
        return error
    raise AssertionError("expected error")


def test_build_report_fields() -> None:
    error = _caught()
    report = build_error_report(
        error, component="extraction", context={"path": "m.txt"}, now=FIXED
    )
    assert report.error_type == "ValueError"
    assert report.message == "boom"
    assert report.component == "extraction"
    assert report.context == {"path": "m.txt"}
    assert report.timestamp == FIXED
    assert report.traceback_summary
    assert any("_raise" in frame for frame in report.traceback_summary)


def test_report_to_dict_is_json_safe() -> None:
    report = build_error_report(_caught(), component="cli", now=FIXED)
    data = report.to_dict()
    assert data["timestamp"] == "2026-03-01T00:00:00Z"
    json.dumps(data)


def test_to_json_deterministic() -> None:
    error = _caught()
    a = build_error_report(error, component="cli", now=FIXED).to_json()
    b = build_error_report(error, component="cli", now=FIXED).to_json()
    assert a == b


def test_frame_limit() -> None:
    error = _caught()
    summary = summarize_traceback(error, limit=1)
    assert len(summary) == 1


def test_no_traceback() -> None:
    error = ValueError("no tb")
    report = build_error_report(error, component="x", now=FIXED)
    assert report.traceback_summary == []
