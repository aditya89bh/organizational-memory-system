"""Deterministic recall benchmarks against fixture data.

Builds a small, fixed in-memory dataset, runs a set of representative recall
queries, and compares the returned record ids against the expected ids. Reports
per-case hit rate and overall top-k accuracy. Fully deterministic and offline.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from organizational_memory.models import (
    Commitment,
    Decision,
    OpenLoop,
    Task,
)
from organizational_memory.models.enums import (
    DecisionStatus,
    OpenLoopStatus,
)
from organizational_memory.recall.decision_search import search_decisions
from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.recall.natural_language import answer
from organizational_memory.recall.query_parser import parse_query
from organizational_memory.recall.task_search import search_tasks
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

TOP_K = 3
PASS_THRESHOLD = 1.0


def build_fixture_store(path: Path) -> MemoryStore:
    """Populate and return a deterministic fixture store."""
    now = utc_now()
    store = JSONStore(path)
    store.save_record(
        Decision(
            id="d1",
            title="Adopt Kubernetes",
            description="run services on kubernetes",
            owner_id="alice",
            status=DecisionStatus.ACCEPTED,
        )
    )
    store.save_record(
        Decision(
            id="d2",
            title="Pricing model",
            description="revisit pricing tiers",
            owner_id="bob",
            status=DecisionStatus.PROPOSED,
        )
    )
    store.save_record(
        Task(id="t1", title="Launch page", description="ship site", owner_id="alice")
    )
    store.save_record(
        Task(id="t2", title="Refactor billing", description="cleanup", owner_id="bob")
    )
    store.save_record(
        OpenLoop(id="o1", question="auth approach?", status=OpenLoopStatus.OPEN)
    )
    store.save_record(
        OpenLoop(id="o2", question="resolved item", status=OpenLoopStatus.RESOLVED)
    )
    store.save_record(
        Commitment(
            id="c1",
            owner_id="bob",
            description="late report",
            created_at=now - timedelta(days=3),
            due_at=now - timedelta(days=1),
        )
    )
    return store


def _keyword_kubernetes(store: MemoryStore) -> list[RecallResult]:
    return search_keywords(store.list_records(), "kubernetes")


def _decision_accepted(store: MemoryStore) -> list[RecallResult]:
    return search_decisions(store, status="accepted")


def _tasks_alice(store: MemoryStore) -> list[RecallResult]:
    return search_tasks(store, owner_id="alice")


def _unresolved(store: MemoryStore) -> list[RecallResult]:
    return answer(store, "What is still unresolved?")


def _overdue(store: MemoryStore) -> list[RecallResult]:
    return answer(store, "What is overdue?", now=utc_now())


def _parser_pricing(store: MemoryStore) -> list[RecallResult]:
    parsed = parse_query("type:decision pricing")
    return search_decisions(store, text=parsed.text)


@dataclass(frozen=True)
class BenchmarkCase:
    """A single benchmark query with its expected result ids."""

    name: str
    expected_ids: tuple[str, ...]
    run: Callable[[MemoryStore], list[RecallResult]]


@dataclass(frozen=True)
class CaseResult:
    """The outcome of running a benchmark case."""

    name: str
    expected_ids: tuple[str, ...]
    returned_ids: tuple[str, ...]

    @property
    def hit_rate(self) -> float:
        if not self.expected_ids:
            return 1.0
        found = sum(1 for rid in self.expected_ids if rid in self.returned_ids)
        return found / len(self.expected_ids)

    @property
    def top_k_hit(self) -> bool:
        top = set(self.returned_ids[:TOP_K])
        return all(rid in top for rid in self.expected_ids)


BENCHMARK_CASES: tuple[BenchmarkCase, ...] = (
    BenchmarkCase("keyword_kubernetes", ("d1",), _keyword_kubernetes),
    BenchmarkCase("decision_accepted", ("d1",), _decision_accepted),
    BenchmarkCase("tasks_alice", ("t1",), _tasks_alice),
    BenchmarkCase("unresolved_open_loops", ("o1",), _unresolved),
    BenchmarkCase("overdue_items", ("c1",), _overdue),
    BenchmarkCase("parser_pricing", ("d2",), _parser_pricing),
)


def run_case(case: BenchmarkCase, store: MemoryStore) -> CaseResult:
    """Execute ``case`` against ``store`` and capture the returned ids."""
    results = case.run(store)
    return CaseResult(
        name=case.name,
        expected_ids=case.expected_ids,
        returned_ids=tuple(result.record.id for result in results),
    )


def run_benchmarks() -> list[CaseResult]:
    """Run every benchmark case against a fresh fixture store."""
    with tempfile.TemporaryDirectory() as tmp:
        store = build_fixture_store(Path(tmp) / "fixture.json")
        return [run_case(case, store) for case in BENCHMARK_CASES]


def overall_hit_rate(results: list[CaseResult]) -> float:
    """Return the mean per-case hit rate."""
    if not results:
        return 0.0
    return sum(result.hit_rate for result in results) / len(results)


def top_k_accuracy(results: list[CaseResult]) -> float:
    """Return the fraction of cases whose expected ids are all in the top-k."""
    if not results:
        return 0.0
    return sum(1 for result in results if result.top_k_hit) / len(results)


def format_report(results: list[CaseResult]) -> str:
    """Render a human-readable benchmark report."""
    lines = ["Recall benchmarks", "================="]
    for result in results:
        lines.append(
            f"{result.name:<22} expected={list(result.expected_ids)} "
            f"returned={list(result.returned_ids)} hit_rate={result.hit_rate:.2f}"
        )
    lines.append(f"Total queries: {len(results)}")
    lines.append(f"Overall hit rate: {overall_hit_rate(results):.2f}")
    lines.append(f"Top-{TOP_K} accuracy: {top_k_accuracy(results):.2f}")
    return "\n".join(lines)


def main() -> int:
    """Run benchmarks, print the report, and return a process exit code."""
    results = run_benchmarks()
    print(format_report(results))
    return 0 if overall_hit_rate(results) >= PASS_THRESHOLD else 1


if __name__ == "__main__":
    raise SystemExit(main())
