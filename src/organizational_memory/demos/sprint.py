"""Sprint planning demo: tasks, commitments, blockers, and a weekly report."""

from datetime import timedelta

from organizational_memory.demos.common import (
    REFERENCE_NOW,
    InMemoryStore,
    heading,
    ingest_meeting,
)
from organizational_memory.reports.weekly_report import weekly_report

TRANSCRIPT = """# Sprint Planning

Attendees: Maria, Sam, Dana

[10:00] Maria: We decided to adopt the new CI pipeline.
[10:02] Sam: I will own the migration to the new runners.
[10:03] Dana: I will write the regression tests.
[10:05] Maria: The rollout is blocked by the staging outage.
[10:06] Sam: Who signs off on the release?
TODO: update the deployment runbook.
Topic: Sprint scope
"""


def run() -> list[str]:
    """Run the sprint planning demo and return deterministic output lines."""
    store = InMemoryStore()
    result = ingest_meeting(
        store, TRANSCRIPT, meeting_id="sprint", title="Sprint Planning"
    )

    lines = ["Sprint planning demo"]
    lines += heading("Extraction")
    lines.append(f"commitments: {len(result.commitments)}")
    lines.append(f"tasks: {len(result.tasks)}")
    lines.append(f"dependencies (blockers): {len(result.dependencies)}")
    lines.append(f"open loops: {len(result.open_loops)}")

    start = REFERENCE_NOW - timedelta(days=7)
    report = weekly_report(store, start=start, end=REFERENCE_NOW, now=REFERENCE_NOW)
    lines += heading("Weekly report")
    lines.append(f"title: {report.title}")
    for key in sorted(report.summary):
        lines.append(f"{key}: {report.summary[key]}")
    return lines
