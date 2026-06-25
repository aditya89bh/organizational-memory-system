"""Shared report construction used by CLI commands.

Maps a report-type name and the relevant options to a concrete
:class:`~organizational_memory.reports.base.Report`, so multiple commands can
build the same reports consistently.
"""

from datetime import datetime

from organizational_memory.reports.base import Report
from organizational_memory.reports.commitment_report import commitment_report
from organizational_memory.reports.decision_report import decision_report
from organizational_memory.reports.follow_up_report import follow_up_report
from organizational_memory.reports.meeting_summary import meeting_summary
from organizational_memory.reports.open_loop_report import open_loop_report
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.reports.weekly_report import weekly_report
from organizational_memory.storage.store import MemoryStore

REPORT_TYPES = (
    "meeting",
    "weekly",
    "follow-up",
    "organizational-memory",
    "decisions",
    "commitments",
    "open-loops",
)


def build_report(
    store: MemoryStore,
    report_type: str,
    *,
    now: datetime,
    start: datetime | None = None,
    end: datetime | None = None,
    meeting_id: str | None = None,
) -> Report:
    """Build the report named ``report_type`` from ``store``.

    Raises ``ValueError`` for unknown types or missing required options.
    """
    if report_type == "meeting":
        if not meeting_id:
            raise ValueError("meeting report requires a meeting id")
        return meeting_summary(store, meeting_id, now=now)
    if report_type == "weekly":
        if start is None or end is None:
            raise ValueError("weekly report requires start and end")
        return weekly_report(store, start=start, end=end, now=now)
    if report_type == "follow-up":
        return follow_up_report(store, now=now)
    if report_type == "organizational-memory":
        return organizational_memory_report(store, now=now)
    if report_type == "decisions":
        return decision_report(store, now=now)
    if report_type == "commitments":
        return commitment_report(store, now=now)
    if report_type == "open-loops":
        return open_loop_report(store, now=now)
    raise ValueError(f"unknown report type: {report_type}")
