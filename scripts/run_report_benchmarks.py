"""Deterministic report generation benchmarks against fixture data.

Builds a small, fixed in-memory dataset, generates every Phase 7 report, and
records the number of sections produced, the export sizes (Markdown, JSON, CSV),
and whether each report contains its expected sections. Fully deterministic and
offline.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

from organizational_memory.models import (
    Commitment,
    Decision,
    Meeting,
    OpenLoop,
    Task,
)
from organizational_memory.models.enums import (
    CommitmentStatus,
    DecisionStatus,
    OpenLoopStatus,
    TaskStatus,
)
from organizational_memory.reports.accountability_report import accountability_report
from organizational_memory.reports.base import Report
from organizational_memory.reports.commitment_report import commitment_report
from organizational_memory.reports.decision_report import decision_report
from organizational_memory.reports.exporters.csv import CSVExporter
from organizational_memory.reports.exporters.json import JSONExporter
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.reports.follow_up_report import follow_up_report
from organizational_memory.reports.meeting_summary import meeting_summary
from organizational_memory.reports.monthly_report import monthly_report
from organizational_memory.reports.open_loop_report import open_loop_report
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.reports.participant_report import participant_report
from organizational_memory.reports.timeline_report import timeline_report
from organizational_memory.reports.weekly_report import weekly_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import parse_timestamp

NOW = parse_timestamp("2026-03-01T00:00:00Z")
WEEK_START = parse_timestamp("2026-02-22T00:00:00Z")
WEEK_END = parse_timestamp("2026-03-01T00:00:00Z")
MONTH_START = parse_timestamp("2026-02-01T00:00:00Z")
MONTH_END = parse_timestamp("2026-03-01T00:00:00Z")


def build_fixture_store(path: Path) -> MemoryStore:
    """Populate and return a deterministic fixture store."""
    store = JSONStore(path)
    store.save_record(
        Meeting(id="m1", title="Kickoff", started_at=NOW - timedelta(days=6),
                participants=["alice", "bob"], source="transcript")
    )
    store.save_record(
        Decision(id="d1", title="Adopt mesh", description="x", owner_id="alice",
                 status=DecisionStatus.ACCEPTED, source_meeting_id="m1",
                 decided_at=NOW - timedelta(days=6),
                 created_at=NOW - timedelta(days=6),
                 rationale="Improves observability.")
    )
    store.save_record(
        Decision(id="d2", title="Pricing", description="x",
                 status=DecisionStatus.PROPOSED,
                 created_at=NOW - timedelta(days=90))
    )
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   status=CommitmentStatus.PENDING, source_meeting_id="m1",
                   created_at=NOW - timedelta(days=6),
                   due_at=NOW - timedelta(days=1))
    )
    store.save_record(
        Task(id="t1", title="provision", description="x", owner_id="bob",
             status=TaskStatus.TODO, source_meeting_id="m1",
             created_at=NOW - timedelta(days=5))
    )
    store.save_record(
        OpenLoop(id="o1", question="scale?", source_meeting_id="m1",
                 status=OpenLoopStatus.OPEN, created_at=NOW - timedelta(days=5))
    )
    return store


@dataclass(frozen=True)
class ReportCase:
    """A single report to benchmark and the sections it must contain."""

    name: str
    expected_sections: tuple[str, ...]
    build: Callable[[MemoryStore], Report]


@dataclass(frozen=True)
class ReportMetrics:
    """The measured outcome of building and exporting one report."""

    name: str
    section_count: int
    markdown_size: int
    json_size: int
    csv_size: int
    missing_sections: tuple[str, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        return not self.missing_sections


REPORT_CASES: tuple[ReportCase, ...] = (
    ReportCase(
        "meeting_summary",
        ("Participants", "Decisions", "Commitments", "Tasks", "Open loops", "Risks"),
        lambda store: meeting_summary(store, "m1", now=NOW),
    ),
    ReportCase(
        "decision_report",
        ("By status", "By owner", "Stale decisions"),
        lambda store: decision_report(store, now=NOW),
    ),
    ReportCase(
        "commitment_report",
        ("Open commitments", "Overdue commitments", "Missing due dates"),
        lambda store: commitment_report(store, now=NOW),
    ),
    ReportCase(
        "open_loop_report",
        ("Unresolved", "Oldest unresolved", "Overdue"),
        lambda store: open_loop_report(store, now=NOW),
    ),
    ReportCase(
        "weekly_report",
        ("Decisions made", "Overdue work", "Memory health"),
        lambda store: weekly_report(store, start=WEEK_START, end=WEEK_END, now=NOW),
    ),
    ReportCase(
        "monthly_report",
        ("Decision velocity", "Accountability summary", "Memory health"),
        lambda store: monthly_report(
            store, start=MONTH_START, end=MONTH_END, now=NOW
        ),
    ),
    ReportCase(
        "timeline_report",
        ("Timeline", "By type"),
        lambda store: timeline_report(store, now=NOW),
    ),
    ReportCase(
        "participant_report",
        ("Meetings attended", "Owned decisions", "Follow-up load"),
        lambda store: participant_report(store, "alice", now=NOW),
    ),
    ReportCase(
        "accountability_report",
        ("Assignment overview", "Owner load", "Follow-through summary"),
        lambda store: accountability_report(store, now=NOW),
    ),
    ReportCase(
        "organizational_memory_report",
        ("Memory health", "Key decisions", "Suggested follow-ups"),
        lambda store: organizational_memory_report(store, now=NOW),
    ),
    ReportCase(
        "follow_up_report",
        ("Needs action", "Unanswered questions", "Next review candidates"),
        lambda store: follow_up_report(store, now=NOW),
    ),
)


def measure_report(case: ReportCase, store: MemoryStore) -> ReportMetrics:
    """Build ``case`` and measure its sections and export sizes."""
    report = case.build(store)
    present = {section.title for section in report.sections}
    missing = tuple(s for s in case.expected_sections if s not in present)
    return ReportMetrics(
        name=case.name,
        section_count=len(report.sections),
        markdown_size=len(MarkdownExporter().export(report)),
        json_size=len(JSONExporter().export(report)),
        csv_size=len(CSVExporter().export(report)),
        missing_sections=missing,
    )


def run_benchmarks() -> list[ReportMetrics]:
    """Build every report against a fresh fixture store and measure it."""
    with tempfile.TemporaryDirectory() as tmp:
        store = build_fixture_store(Path(tmp) / "fixture.json")
        return [measure_report(case, store) for case in REPORT_CASES]


def total_sections(results: list[ReportMetrics]) -> int:
    """Return the total number of generated sections across all reports."""
    return sum(result.section_count for result in results)


def all_passed(results: list[ReportMetrics]) -> bool:
    """Return whether every report contained its expected sections."""
    return all(result.passed for result in results)


def format_report(results: list[ReportMetrics]) -> str:
    """Render a human-readable benchmark report."""
    lines = ["Report benchmarks", "================="]
    for result in results:
        status = "ok" if result.passed else f"MISSING {list(result.missing_sections)}"
        lines.append(
            f"{result.name:<30} sections={result.section_count} "
            f"md={result.markdown_size} json={result.json_size} "
            f"csv={result.csv_size} {status}"
        )
    lines.append(f"Reports: {len(results)}")
    lines.append(f"Total sections: {total_sections(results)}")
    lines.append(f"Pass: {all_passed(results)}")
    return "\n".join(lines)


def main() -> int:
    """Run benchmarks, print the report, and return a process exit code."""
    results = run_benchmarks()
    print(format_report(results))
    return 0 if all_passed(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
