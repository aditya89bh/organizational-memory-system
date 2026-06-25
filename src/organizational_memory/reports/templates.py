"""Reusable deterministic report templates.

Templates curate existing reports into focused, audience-specific views by
selecting and relabeling a subset of sections. They add no new computation; they
recompose deterministic report builders so the same inputs always yield the same
templated output.
"""

from datetime import datetime

from organizational_memory.reports.base import Report
from organizational_memory.reports.follow_up_report import follow_up_report
from organizational_memory.reports.meeting_summary import meeting_summary
from organizational_memory.reports.open_loop_report import open_loop_report
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.reports.weekly_report import weekly_report
from organizational_memory.storage.store import MemoryStore


def select_sections(source: Report, titles: tuple[str, ...], *, title: str) -> Report:
    """Return a new report containing only ``titles`` from ``source``.

    Missing section titles are skipped. Summary and metadata are carried over so
    the templated report stays self-describing.
    """
    sections = [
        section
        for wanted in titles
        if (section := source.section(wanted)) is not None
    ]
    return Report(
        title=title,
        generated_at=source.generated_at,
        summary=dict(source.summary),
        sections=sections,
        metadata=dict(source.metadata),
    )


def executive_summary(store: MemoryStore, *, now: datetime | None = None) -> Report:
    """Curate a concise executive summary from the memory report."""
    source = organizational_memory_report(store, now=now)
    return select_sections(
        source,
        ("Memory health", "Key decisions", "Unresolved loops", "Bottlenecks"),
        title="Executive summary",
    )


def meeting_summary_template(
    store: MemoryStore,
    meeting_id: str,
    *,
    now: datetime | None = None,
) -> Report:
    """Curate a meeting summary focused on outcomes."""
    source = meeting_summary(store, meeting_id, now=now)
    return select_sections(
        source,
        ("Participants", "Decisions", "Commitments", "Open loops"),
        title=source.title,
    )


def weekly_review(
    store: MemoryStore,
    *,
    start: datetime,
    end: datetime,
    now: datetime | None = None,
) -> Report:
    """Curate a weekly review from the full weekly report."""
    source = weekly_report(store, start=start, end=end, now=now)
    return select_sections(
        source,
        ("Decisions made", "Commitments", "Open loops", "Overdue work",
         "Memory health"),
        title="Weekly review",
    )


def open_loop_review(store: MemoryStore, *, now: datetime | None = None) -> Report:
    """Curate an open-loop review focused on unresolved and overdue items."""
    source = open_loop_report(store, now=now)
    return select_sections(
        source,
        ("Unresolved", "Oldest unresolved", "Overdue"),
        title="Open-loop review",
    )


def follow_up_memo(store: MemoryStore, *, now: datetime | None = None) -> Report:
    """Curate a follow-up memo from the full follow-up report."""
    source = follow_up_report(store, now=now)
    return select_sections(
        source,
        ("Needs action", "Due dates", "Unanswered questions",
         "Next review candidates"),
        title="Follow-up memo",
    )
