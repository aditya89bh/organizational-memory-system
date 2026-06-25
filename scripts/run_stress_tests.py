"""Deterministic stress tests for edge workloads.

Each scenario exercises a boundary condition (empty input, very long lines,
duplicate records, many owners, many open loops, large reports, and extreme
pagination) and reports a pass/fail with a short detail. Everything runs
in-process with no network access.

Usage::

    python scripts/run_stress_tests.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from organizational_memory.demos.common import (
    REFERENCE_NOW,
    InMemoryStore,
    ingest_meeting,
)
from organizational_memory.extraction.errors import EmptyTranscriptError
from organizational_memory.extraction.pipeline import run_extraction
from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.utils.time import parse_timestamp

_BASE_TIME = parse_timestamp("2026-01-01T00:00:00Z")


@dataclass(frozen=True)
class ScenarioResult:
    """The outcome of a single stress scenario."""

    name: str
    passed: bool
    detail: str


def scenario_empty_transcript() -> ScenarioResult:
    try:
        run_extraction("")
    except EmptyTranscriptError:
        return ScenarioResult("empty_transcript", True, "raised EmptyTranscriptError")
    return ScenarioResult("empty_transcript", False, "did not raise")


def scenario_very_long_lines() -> ScenarioResult:
    long_line = "word " * 4000
    transcript = (
        "Alice: We decided to adopt the rollout plan.\n"
        f"Bob: {long_line}\n"
        "Carol: I will follow up by Friday."
    )
    result = run_extraction(transcript)
    passed = len(result.decisions) >= 1
    return ScenarioResult(
        "very_long_lines", passed, f"decisions={len(result.decisions)}"
    )


def scenario_duplicate_records() -> ScenarioResult:
    store = InMemoryStore()
    record = Decision(
        id="dup",
        title="Duplicate",
        description="Same record saved repeatedly.",
        owner_id="alice",
        status=DecisionStatus.ACCEPTED,
        created_at=_BASE_TIME,
        updated_at=_BASE_TIME,
    )
    for _ in range(100):
        store.save_record(record)
    deduped = len(store.list_records()) == 1
    for index in range(100):
        store.save_record(
            Decision(
                id=f"unique-{index}",
                title=f"Decision {index}",
                description="Unique record.",
                owner_id="alice",
                status=DecisionStatus.ACCEPTED,
                created_at=_BASE_TIME,
                updated_at=_BASE_TIME,
            )
        )
    grew = len(store.list_records()) == 101
    return ScenarioResult(
        "duplicate_records", deduped and grew, f"count={len(store.list_records())}"
    )


def scenario_many_owners() -> ScenarioResult:
    lines = [
        f"User{index}: I will deliver task {index} by Friday." for index in range(60)
    ]
    result = run_extraction("\n".join(lines))
    passed = len(result.commitments) >= 1
    return ScenarioResult(
        "many_owners", passed, f"commitments={len(result.commitments)}"
    )


def scenario_many_open_loops() -> ScenarioResult:
    lines = [
        f"Alice: Open question: should we resolve issue {index}?"
        for index in range(60)
    ]
    result = run_extraction("\n".join(lines))
    passed = len(result.open_loops) >= 1
    return ScenarioResult(
        "many_open_loops", passed, f"open_loops={len(result.open_loops)}"
    )


def scenario_many_report_sections() -> ScenarioResult:
    store = InMemoryStore()
    for index in range(20):
        ingest_meeting(
            store,
            (
                f"Alice: We decided to adopt plan {index}.\n"
                f"Bob: I will deliver module {index} by Friday.\n"
                f"Carol: Open question: do we need budget {index}?"
            ),
            meeting_id=f"meeting-{index}",
            title=f"Meeting {index}",
        )
    report = organizational_memory_report(store, now=REFERENCE_NOW)
    passed = len(report.sections) >= 1
    return ScenarioResult(
        "many_report_sections", passed, f"sections={len(report.sections)}"
    )


def scenario_pagination_extremes() -> ScenarioResult:
    store = InMemoryStore()
    ingest_meeting(
        store,
        "Alice: I will deliver module one by Friday.",
        meeting_id="m",
        title="M",
    )
    records = search_keywords(store.list_records(), "module")
    beyond = records[10_000:]
    everything = records[0:10_000]
    passed = beyond == [] and len(everything) == len(records)
    return ScenarioResult(
        "pagination_extremes", passed, f"records={len(records)}"
    )


def run_all() -> list[ScenarioResult]:
    """Run every stress scenario and return the results."""
    return [
        scenario_empty_transcript(),
        scenario_very_long_lines(),
        scenario_duplicate_records(),
        scenario_many_owners(),
        scenario_many_open_loops(),
        scenario_many_report_sections(),
        scenario_pagination_extremes(),
    ]


def format_report(results: list[ScenarioResult]) -> str:
    """Build a human-readable stress test report."""
    lines = ["Stress tests", ""]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"  {status} {result.name}: {result.detail}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Run all stress scenarios and print a report."""
    results = run_all()
    print(format_report(results))
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
