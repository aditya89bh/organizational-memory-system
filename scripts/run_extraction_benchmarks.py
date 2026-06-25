"""Deterministic extraction benchmark over the bundled sample transcripts.

The benchmark loads each example transcript, runs the extraction pipeline, and
compares the number of records produced per category against known-good
expected counts. It prints a small report and exits non-zero when the overall
category accuracy falls below :data:`PASS_THRESHOLD`.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from organizational_memory.extraction.pipeline import ExtractionResult, run_extraction
from organizational_memory.ingestion.markdown_loader import load_markdown_from_file
from organizational_memory.ingestion.transcript_loader import (
    load_transcript_from_file,
)

CATEGORIES: tuple[str, ...] = (
    "participants",
    "decisions",
    "commitments",
    "tasks",
    "open_loops",
    "dependencies",
    "risks",
    "action_items",
    "topics",
)

PASS_THRESHOLD = 0.8

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "transcripts"


@dataclass(frozen=True)
class BenchmarkCase:
    """A single benchmark fixture and its expected per-category counts."""

    filename: str
    is_markdown: bool
    expected: dict[str, int]


@dataclass(frozen=True)
class CaseResult:
    """The outcome of running one benchmark case."""

    filename: str
    expected: dict[str, int]
    actual: dict[str, int]

    @property
    def matched(self) -> int:
        """Number of categories whose actual count equals the expected count."""
        return sum(
            1 for name in CATEGORIES if self.expected[name] == self.actual[name]
        )


BENCHMARK_CASES: tuple[BenchmarkCase, ...] = (
    BenchmarkCase(
        filename="startup_product_meeting.txt",
        is_markdown=False,
        expected={
            "participants": 3,
            "decisions": 1,
            "commitments": 2,
            "tasks": 2,
            "open_loops": 2,
            "dependencies": 1,
            "risks": 1,
            "action_items": 4,
            "topics": 0,
        },
    ),
    BenchmarkCase(
        filename="sprint_planning_meeting.md",
        is_markdown=True,
        expected={
            "participants": 3,
            "decisions": 2,
            "commitments": 2,
            "tasks": 2,
            "open_loops": 2,
            "dependencies": 1,
            "risks": 1,
            "action_items": 4,
            "topics": 8,
        },
    ),
    BenchmarkCase(
        filename="board_review_meeting.txt",
        is_markdown=False,
        expected={
            "participants": 3,
            "decisions": 2,
            "commitments": 1,
            "tasks": 1,
            "open_loops": 1,
            "dependencies": 1,
            "risks": 2,
            "action_items": 2,
            "topics": 0,
        },
    ),
)


def count_records(result: ExtractionResult) -> dict[str, int]:
    """Return the number of extracted records per category."""
    return {name: len(getattr(result, name)) for name in CATEGORIES}


def run_case(case: BenchmarkCase, base_dir: Path = EXAMPLES_DIR) -> CaseResult:
    """Run extraction for a single benchmark case."""
    path = base_dir / case.filename
    loader = load_markdown_from_file if case.is_markdown else load_transcript_from_file
    result = run_extraction(loader(path))
    return CaseResult(
        filename=case.filename,
        expected=dict(case.expected),
        actual=count_records(result),
    )


def category_accuracy(results: list[CaseResult]) -> float:
    """Return the fraction of categories that matched across all cases."""
    total = len(results) * len(CATEGORIES)
    if total == 0:
        return 0.0
    matched = sum(result.matched for result in results)
    return matched / total


def format_report(results: list[CaseResult]) -> str:
    """Build a human-readable benchmark report."""
    lines = [f"Total files: {len(results)}"]
    for result in results:
        lines.append(f"\n{result.filename}")
        for name in CATEGORIES:
            expected = result.expected[name]
            actual = result.actual[name]
            flag = "ok" if expected == actual else "MISMATCH"
            lines.append(
                f"  {name:<14} expected={expected:<3} actual={actual:<3} {flag}"
            )
    accuracy = category_accuracy(results)
    lines.append(
        f"\nCategory accuracy: {accuracy:.2%} (threshold {PASS_THRESHOLD:.0%})"
    )
    lines.append("PASS" if accuracy >= PASS_THRESHOLD else "FAIL")
    return "\n".join(lines)


def main() -> int:
    """Run all benchmark cases and print a report."""
    results = [run_case(case) for case in BENCHMARK_CASES]
    print(format_report(results))
    return 0 if category_accuracy(results) >= PASS_THRESHOLD else 1


if __name__ == "__main__":
    sys.exit(main())
