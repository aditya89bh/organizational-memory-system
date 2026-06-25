"""Tutorial 3: run analytics and generate reports.

Run it with::

    python examples/tutorials/tutorial_03_analytics_and_reports.py

This tutorial builds a small store from a transcript, runs deterministic
analytics over it, generates an organizational-memory report at a fixed reference
time, and renders that report to Markdown. No network is used.
"""

import tempfile
from datetime import UTC, datetime
from pathlib import Path

from organizational_memory.analytics.reporting import generate_report
from organizational_memory.extraction.pipeline import ExtractionResult, run_extraction
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.json_store import JSONStore

NOW = datetime(2026, 3, 1, tzinfo=UTC)
TRANSCRIPT = """# Leadership Review

[14:00] Aditya: We decided to expand into the European market.
[14:03] Lena: I will draft the hiring plan.
[14:05] Marcus: The expansion is blocked by regulatory approval.
[14:07] Aditya: What is our compliance timeline?
Risk: currency exposure could reduce margins.
"""

_GROUPS = (
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


def persist(store: JSONStore, result: ExtractionResult) -> None:
    for attr in _GROUPS:
        records: list[BaseRecord] = getattr(result, attr)
        for record in records:
            store.save_record(record)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        persist(store, run_extraction(TRANSCRIPT))

        analytics = generate_report(store, now=NOW)
        print(f"Analytics summary groups: {len(analytics.summary)}")

        report = organizational_memory_report(store, now=NOW)
        print(f"Report sections: {len(report.sections)}")

        markdown = MarkdownExporter().export(report)
        print("\nReport (first lines):")
        for line in markdown.splitlines()[:6]:
            print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
