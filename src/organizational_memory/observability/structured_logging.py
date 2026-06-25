"""Structured, JSON-safe logging events.

A :class:`LogEvent` is an immutable, JSON-serializable record describing a single
log entry: when it happened, its level, the emitting component, an event name, an
optional trace identifier, and arbitrary metadata. :class:`StructuredLogger`
builds events deterministically and can optionally write them as JSON lines to a
text stream. There is no network access.
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TextIO

from organizational_memory.utils.serialization import to_json, to_serializable
from organizational_memory.utils.time import format_timestamp, utc_now

LOG_LEVELS: tuple[str, ...] = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
_VALID_LEVELS = frozenset(LOG_LEVELS)


def _normalize_level(level: str) -> str:
    candidate = level.upper()
    if candidate not in _VALID_LEVELS:
        raise ValueError(
            f"invalid log level {level!r}; expected one of {list(LOG_LEVELS)}"
        )
    return candidate


@dataclass(frozen=True)
class LogEvent:
    """An immutable, JSON-safe structured log event."""

    timestamp: datetime
    level: str
    component: str
    event: str
    trace_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping for this event."""
        return {
            "timestamp": format_timestamp(self.timestamp),
            "level": self.level,
            "component": self.component,
            "event": self.event,
            "trace_id": self.trace_id,
            "metadata": to_serializable(self.metadata),
        }

    def to_json(self) -> str:
        """Return a deterministic JSON string for this event."""
        return to_json(self.to_dict(), sort_keys=True)


class StructuredLogger:
    """Builds and optionally emits :class:`LogEvent` records."""

    def __init__(
        self,
        component: str,
        *,
        stream: TextIO | None = None,
        clock: Callable[[], datetime] = utc_now,
        trace_id: str | None = None,
    ) -> None:
        self.component = component
        self._stream = stream
        self._clock = clock
        self._trace_id = trace_id

    def log(
        self,
        level: str,
        event: str,
        *,
        trace_id: str | None = None,
        now: datetime | None = None,
        **metadata: Any,
    ) -> LogEvent:
        """Build a :class:`LogEvent`, emit it if a stream is set, and return it."""
        record = LogEvent(
            timestamp=now if now is not None else self._clock(),
            level=_normalize_level(level),
            component=self.component,
            event=event,
            trace_id=trace_id if trace_id is not None else self._trace_id,
            metadata=dict(metadata),
        )
        if self._stream is not None:
            self._stream.write(record.to_json() + "\n")
        return record

    def debug(self, event: str, **metadata: Any) -> LogEvent:
        return self.log("DEBUG", event, **metadata)

    def info(self, event: str, **metadata: Any) -> LogEvent:
        return self.log("INFO", event, **metadata)

    def warning(self, event: str, **metadata: Any) -> LogEvent:
        return self.log("WARNING", event, **metadata)

    def error(self, event: str, **metadata: Any) -> LogEvent:
        return self.log("ERROR", event, **metadata)

    def critical(self, event: str, **metadata: Any) -> LogEvent:
        return self.log("CRITICAL", event, **metadata)


def default_stream() -> TextIO:
    """Return the default log stream (standard error)."""
    return sys.stderr
