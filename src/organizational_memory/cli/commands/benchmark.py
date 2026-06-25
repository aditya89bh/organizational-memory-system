"""``benchmark`` command: run deterministic benchmarks from the CLI."""

import argparse
import importlib.util
import sys
from pathlib import Path

from organizational_memory.analytics.reporting import generate_report
from organizational_memory.demos import board, sprint, startup
from organizational_memory.demos.common import (
    REFERENCE_NOW,
    InMemoryStore,
    ingest_meeting,
)

_SCRIPT_BENCHMARKS: dict[str, str] = {
    "extraction": "run_extraction_benchmarks.py",
    "recall": "run_recall_benchmarks.py",
    "reports": "run_report_benchmarks.py",
}
_TYPES = ("extraction", "recall", "reports", "analytics", "all")


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``benchmark`` subcommand."""
    parser = subparsers.add_parser(
        "benchmark",
        help="Run deterministic benchmarks.",
        description="Run extraction, recall, reports, or analytics benchmarks.",
    )
    parser.add_argument("type", choices=_TYPES, help="Benchmark to run.")
    parser.set_defaults(handler=run)


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parents[4] / "scripts"


def _run_script(name: str) -> int:
    path = _scripts_dir() / _SCRIPT_BENCHMARKS[name]
    if not path.exists():
        print(f"error: benchmark script not found: {path}")
        return 1
    spec = importlib.util.spec_from_file_location(f"benchmark_{name}", path)
    if spec is None or spec.loader is None:
        print(f"error: cannot load benchmark script: {path}")
        return 1
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return int(module.main())
    finally:
        sys.modules.pop(spec.name, None)


def _run_analytics() -> int:
    store = InMemoryStore()
    ingest_meeting(store, startup.TRANSCRIPT, meeting_id="startup", title="Startup")
    ingest_meeting(store, sprint.TRANSCRIPT, meeting_id="sprint", title="Sprint")
    ingest_meeting(store, board.TRANSCRIPT, meeting_id="board", title="Board")
    report = generate_report(store, now=REFERENCE_NOW)
    print("Analytics benchmark")
    print(f"  records: {len(store.list_records())}")
    print(f"  summary_metrics: {len(report.summary)}")
    print(f"  key_metrics: {len(report.key_metrics)}")
    print(f"  owners_tracked: {len(report.owner_load)}")
    print(f"  health_grade: {report.summary['health_grade']}")
    return 0


def _run_one(name: str) -> int:
    if name == "analytics":
        return _run_analytics()
    return _run_script(name)


def run(args: argparse.Namespace) -> int:
    """Execute the ``benchmark`` command."""
    if args.type != "all":
        return _run_one(args.type)

    exit_code = 0
    for index, name in enumerate(("extraction", "recall", "reports", "analytics")):
        if index:
            print()
        result = _run_one(name)
        exit_code = exit_code or result
    return exit_code
