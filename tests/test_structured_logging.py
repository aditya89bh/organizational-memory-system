"""Tests for structured logging."""

import io
import json

import pytest

from organizational_memory.observability.structured_logging import (
    LOG_LEVELS,
    LogEvent,
    StructuredLogger,
)
from organizational_memory.utils.time import parse_timestamp

FIXED = parse_timestamp("2026-03-01T00:00:00Z")


def _clock() -> object:
    return FIXED


def test_event_to_dict_is_json_safe() -> None:
    event = LogEvent(
        timestamp=FIXED, level="INFO", component="cli", event="started",
        trace_id="t1", metadata={"count": 3},
    )
    data = event.to_dict()
    assert data["timestamp"] == "2026-03-01T00:00:00Z"
    assert data["level"] == "INFO"
    assert data["metadata"] == {"count": 3}
    json.dumps(data)


def test_logger_emits_json_line() -> None:
    stream = io.StringIO()
    logger = StructuredLogger("cli", stream=stream, clock=_clock)  # type: ignore[arg-type]
    event = logger.info("ingest", records=5)
    assert event.level == "INFO"
    assert event.timestamp == FIXED
    line = stream.getvalue().strip()
    loaded = json.loads(line)
    assert loaded["component"] == "cli"
    assert loaded["event"] == "ingest"
    assert loaded["metadata"]["records"] == 5


def test_logger_levels() -> None:
    logger = StructuredLogger("x", clock=_clock)  # type: ignore[arg-type]
    assert logger.debug("d").level == "DEBUG"
    assert logger.warning("w").level == "WARNING"
    assert logger.error("e").level == "ERROR"
    assert logger.critical("c").level == "CRITICAL"


def test_invalid_level_raises() -> None:
    logger = StructuredLogger("x")
    with pytest.raises(ValueError, match="invalid log level"):
        logger.log("trace", "event")


def test_trace_id_default_and_override() -> None:
    logger = StructuredLogger("x", clock=_clock, trace_id="base")  # type: ignore[arg-type]
    assert logger.info("a").trace_id == "base"
    assert logger.info("b", trace_id="override").trace_id == "override"


def test_levels_constant() -> None:
    assert LOG_LEVELS == ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def test_to_json_is_deterministic() -> None:
    logger = StructuredLogger("x", clock=_clock)  # type: ignore[arg-type]
    first = logger.info("evt", a=1, b=2).to_json()
    second = logger.info("evt", b=2, a=1).to_json()
    assert first == second
