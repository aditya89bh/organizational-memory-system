"""Deterministic, local error reports.

Turns a caught exception into an immutable, JSON-serializable
:class:`ErrorReport` describing the error type, message, originating component, a
compact traceback summary, context metadata, and a timestamp. Reports are built
in-process and are never sent to an external service.
"""

import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from organizational_memory.utils.serialization import to_json, to_serializable
from organizational_memory.utils.time import format_timestamp, utc_now

DEFAULT_FRAME_LIMIT = 5


def summarize_traceback(
    error: BaseException, *, limit: int = DEFAULT_FRAME_LIMIT
) -> list[str]:
    """Return the last ``limit`` traceback frames as ``file:line in func`` lines."""
    frames = traceback.extract_tb(error.__traceback__)
    summary = [
        f"{frame.filename}:{frame.lineno} in {frame.name}" for frame in frames
    ]
    if limit >= 0:
        summary = summary[-limit:]
    return summary


@dataclass(frozen=True)
class ErrorReport:
    """An immutable, JSON-safe description of a single error."""

    timestamp: datetime
    error_type: str
    message: str
    component: str
    traceback_summary: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping for this report."""
        return {
            "timestamp": format_timestamp(self.timestamp),
            "error_type": self.error_type,
            "message": self.message,
            "component": self.component,
            "traceback_summary": list(self.traceback_summary),
            "context": to_serializable(self.context),
        }

    def to_json(self) -> str:
        """Return a deterministic JSON string for this report."""
        return to_json(self.to_dict(), sort_keys=True)


def build_error_report(
    error: BaseException,
    *,
    component: str,
    context: dict[str, Any] | None = None,
    now: datetime | None = None,
    frame_limit: int = DEFAULT_FRAME_LIMIT,
) -> ErrorReport:
    """Build an :class:`ErrorReport` from ``error``."""
    return ErrorReport(
        timestamp=now if now is not None else utc_now(),
        error_type=type(error).__name__,
        message=str(error),
        component=component,
        traceback_summary=summarize_traceback(error, limit=frame_limit),
        context=dict(context or {}),
    )
