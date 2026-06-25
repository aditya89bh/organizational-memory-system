"""Local, deterministic observability helpers.

Provides structured logging and local error reporting. Nothing here performs
network calls or talks to external services; everything is in-process and
JSON-serializable for local inspection and testing.
"""

from organizational_memory.observability.structured_logging import (
    LOG_LEVELS,
    LogEvent,
    StructuredLogger,
)

__all__ = ["LOG_LEVELS", "LogEvent", "StructuredLogger"]
