"""Board meeting demo: decisions, risks, and organizational memory reports."""

from organizational_memory.demos.common import (
    REFERENCE_NOW,
    InMemoryStore,
    heading,
    ingest_meeting,
)
from organizational_memory.reports.decision_report import decision_report
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)

TRANSCRIPT = """# Board Review

Attendees: Aditya, Lena, Marcus

[14:00] Aditya: We decided to expand into the European market.
[14:03] Lena: We decided to hire a new head of sales.
[14:05] Marcus: The expansion is blocked by regulatory approval.
[14:07] Aditya: What is our compliance timeline?
Risk: currency exposure could reduce margins.
Risk: hiring delays may slow the expansion.
Topic: Market expansion
"""


def run() -> list[str]:
    """Run the board meeting demo and return deterministic output lines."""
    store = InMemoryStore()
    result = ingest_meeting(store, TRANSCRIPT, meeting_id="board", title="Board Review")

    lines = ["Board meeting demo"]
    lines += heading("Extraction")
    lines.append(f"decisions: {len(result.decisions)}")
    lines.append(f"risks: {len(result.risks)}")
    lines.append(f"open loops: {len(result.open_loops)}")

    decisions = decision_report(store, now=REFERENCE_NOW)
    lines += heading("Decision report")
    lines.append(f"title: {decisions.title}")
    for key in sorted(decisions.summary):
        lines.append(f"{key}: {decisions.summary[key]}")

    memory = organizational_memory_report(store, now=REFERENCE_NOW)
    lines += heading("Organizational memory report")
    lines.append(f"title: {memory.title}")
    for key in sorted(memory.summary):
        lines.append(f"{key}: {memory.summary[key]}")
    return lines
