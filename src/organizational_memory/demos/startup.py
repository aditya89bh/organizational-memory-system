"""Startup meeting demo: ingest, extract, persist, and follow up."""

from organizational_memory.demos.common import (
    REFERENCE_NOW,
    InMemoryStore,
    heading,
    ingest_meeting,
)
from organizational_memory.reports.follow_up_report import follow_up_report

TRANSCRIPT = """# Startup Standup

Attendees: Aditya, Priya, Rahul

[09:00] Aditya: We decided to delay the launch to next month.
[09:02] Priya: I will finalize the pricing page.
[09:04] Rahul: The launch is blocked by the security review.
[09:05] Aditya: What is our runway?
Risk: we might run out of cash before the next round.
TODO: prepare the investor update.
Topic: Launch delay
"""


def run() -> list[str]:
    """Run the startup meeting demo and return deterministic output lines."""
    store = InMemoryStore()
    result = ingest_meeting(
        store, TRANSCRIPT, meeting_id="startup", title="Startup Standup"
    )

    lines = ["Startup meeting demo"]
    lines += heading("Extraction")
    lines.append(f"participants: {len(result.participants)}")
    lines.append(f"decisions: {len(result.decisions)}")
    lines.append(f"commitments: {len(result.commitments)}")
    lines.append(f"tasks: {len(result.tasks)}")
    lines.append(f"open loops: {len(result.open_loops)}")
    lines.append(f"risks: {len(result.risks)}")

    report = follow_up_report(store, now=REFERENCE_NOW)
    lines += heading("Follow-up report")
    lines.append(f"title: {report.title}")
    for key in sorted(report.summary):
        lines.append(f"{key}: {report.summary[key]}")
    return lines
