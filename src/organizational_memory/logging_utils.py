"""Centralized logging configuration.

Provides a single place to configure the package logger and a helper to obtain
namespaced child loggers.
"""

import logging
import sys
from typing import TextIO

from organizational_memory import constants

DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger namespaced under the application root logger."""
    if name:
        return logging.getLogger(f"{constants.APP_NAME}.{name}")
    return logging.getLogger(constants.APP_NAME)


def configure_logging(
    level: int | str = "INFO",
    *,
    stream: TextIO | None = None,
    fmt: str = DEFAULT_LOG_FORMAT,
) -> logging.Logger:
    """Configure and return the application root logger.

    Replaces any previously attached handlers so the function is idempotent and
    safe to call multiple times.
    """
    logger = get_logger()
    logger.setLevel(level)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    stream_handler = logging.StreamHandler(stream if stream is not None else sys.stderr)
    stream_handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger
