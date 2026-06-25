"""Shared helpers for report construction.

Small utilities reused across period-based reports: half-open time-window
membership and a standard ``key``/``count`` table builder.
"""

from datetime import datetime

from organizational_memory.reports.base import ReportTable
from organizational_memory.utils.time import format_timestamp


def in_window(
    moment: datetime | None,
    start: datetime,
    end: datetime,
) -> bool:
    """Return whether ``moment`` falls in the half-open window ``[start, end)``."""
    if moment is None:
        return False
    return start <= moment < end


def window_label(start: datetime, end: datetime) -> str:
    """Return a human-readable label for a reporting window."""
    return f"{format_timestamp(start)} .. {format_timestamp(end)}"


def counts_table(title: str, counts: dict[str, int]) -> ReportTable:
    """Build a two-column ``key``/``count`` table from ``counts``."""
    return ReportTable(
        title=title,
        columns=("key", "count"),
        rows=[(key, str(value)) for key, value in counts.items()],
    )
