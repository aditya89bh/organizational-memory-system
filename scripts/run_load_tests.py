"""Deterministic local load tests.

Exercises the pipeline at volume entirely in-process: it ingests many synthetic
transcripts, persists the extracted records, runs recall across all of them, and
generates reports over the full set. There is no network access and no external
service; "load" here means many records, not concurrent clients.

Usage::

    python scripts/run_load_tests.py 100
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from organizational_memory.analytics.reporting import generate_report
from organizational_memory.demos.common import (
    REFERENCE_NOW,
    InMemoryStore,
    ingest_meeting,
)
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)

DEFAULT_MEETINGS = 50
_OWNERS = ("Alice", "Bob", "Carol", "Dave")


def generate_transcript(index: int) -> str:
    """Return a deterministic synthetic transcript for meeting ``index``."""
    owner = _OWNERS[index % len(_OWNERS)]
    other = _OWNERS[(index + 1) % len(_OWNERS)]
    return "\n".join(
        [
            f"{owner}: We decided to adopt plan {index} for the launch.",
            f"{other}: I will deliver module {index} by next Friday.",
            f"{owner}: Action item: {other} to review report {index}.",
            f"{other}: Open question: do we need approval for budget {index}?",
        ]
    )


def ingest_many(count: int) -> InMemoryStore:
    """Ingest ``count`` synthetic transcripts into a fresh in-memory store."""
    store = InMemoryStore()
    for index in range(count):
        ingest_meeting(
            store,
            generate_transcript(index),
            meeting_id=f"meeting-{index}",
            title=f"Meeting {index}",
        )
    return store


@dataclass(frozen=True)
class LoadTestResult:
    """Aggregate results of a load test run."""

    meetings: int
    records_persisted: int
    recall_hits: int
    report_sections: int


def run(count: int = DEFAULT_MEETINGS) -> LoadTestResult:
    """Run the load test over ``count`` synthetic meetings."""
    store = ingest_many(count)
    records = store.list_records()
    hits = search_keywords(records, "module")
    generate_report(store, now=REFERENCE_NOW)
    report = organizational_memory_report(store, now=REFERENCE_NOW)
    return LoadTestResult(
        meetings=count,
        records_persisted=len(records),
        recall_hits=len(hits),
        report_sections=len(report.sections),
    )


def format_report(result: LoadTestResult) -> str:
    """Build a human-readable load test report."""
    return "\n".join(
        [
            "Load test",
            "",
            f"  meetings: {result.meetings}",
            f"  records_persisted: {result.records_persisted}",
            f"  recall_hits: {result.recall_hits}",
            f"  report_sections: {result.report_sections}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    """Run the load test and print a report."""
    count = DEFAULT_MEETINGS
    if argv:
        count = int(argv[0])
    print(format_report(run(count)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
