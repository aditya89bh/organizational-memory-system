"""Tests for logging utilities."""

import io
import logging

from organizational_memory import constants
from organizational_memory.logging_utils import configure_logging, get_logger


def test_get_logger_namespaces_under_app() -> None:
    assert get_logger().name == constants.APP_NAME
    assert get_logger("ingest").name == f"{constants.APP_NAME}.ingest"


def test_configure_logging_is_idempotent() -> None:
    first = configure_logging("INFO")
    second = configure_logging("DEBUG")
    assert first is second
    assert len(second.handlers) == 1
    assert second.level == logging.DEBUG


def test_configure_logging_writes_to_stream() -> None:
    stream = io.StringIO()
    logger = configure_logging("INFO", stream=stream)
    logger.info("hello memory")
    assert "hello memory" in stream.getvalue()
