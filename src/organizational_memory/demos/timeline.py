"""Organizational timeline demo: multiple meetings over time."""

from datetime import UTC, datetime

from organizational_memory.analytics.timeline_analytics import timeline_analytics
from organizational_memory.demos.common import (
    InMemoryStore,
    heading,
    ingest_meeting,
)
from organizational_memory.reports.timeline_report import timeline_report

KICKOFF = """# Kickoff

Attendees: Aditya, Priya

[09:00] Aditya: We decided to start the platform rebuild.
[09:02] Priya: I will draft the architecture proposal.
Topic: Platform rebuild
"""

MIDPOINT = """# Midpoint Review

Attendees: Aditya, Rahul

[09:00] Aditya: We decided to extend the timeline by two weeks.
[09:02] Rahul: The rebuild is blocked by the data migration.
[09:03] Rahul: What is the cutover plan?
Topic: Timeline extension
"""

WRAP_UP = """# Wrap Up

Attendees: Priya, Rahul

[09:00] Priya: We decided to ship the rebuild to production.
[09:02] Rahul: I will monitor the rollout.
Topic: Production launch
"""


def run() -> list[str]:
    """Run the organizational timeline demo and return deterministic lines."""
    store = InMemoryStore()
    ingest_meeting(
        store, KICKOFF, meeting_id="kickoff", title="Kickoff",
        when=datetime(2026, 1, 12, 9, 0, tzinfo=UTC),
    )
    ingest_meeting(
        store, MIDPOINT, meeting_id="midpoint", title="Midpoint Review",
        when=datetime(2026, 2, 9, 9, 0, tzinfo=UTC),
    )
    ingest_meeting(
        store, WRAP_UP, meeting_id="wrapup", title="Wrap Up",
        when=datetime(2026, 3, 2, 9, 0, tzinfo=UTC),
    )

    lines = ["Organizational timeline demo"]
    analytics = timeline_analytics(store)
    lines += heading("Timeline analytics")
    lines.append(f"total records: {analytics.total}")
    lines.append(f"first date: {analytics.first_date}")
    lines.append(f"last date: {analytics.last_date}")
    lines.append(f"busiest date: {analytics.busiest_date} ({analytics.busiest_count})")

    report = timeline_report(store)
    lines += heading("Timeline report")
    lines.append(f"title: {report.title}")
    lines.append(f"sections: {len(report.sections)}")
    return lines
