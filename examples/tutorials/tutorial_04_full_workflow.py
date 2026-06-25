"""Tutorial 4: the full workflow end to end.

Run it with::

    python examples/tutorials/tutorial_04_full_workflow.py

This tutorial ties the previous tutorials together: ingest two transcripts,
persist them, recall across the combined memory, run analytics, and generate a
report — all deterministically and with no network access.
"""

import tempfile
from datetime import UTC, datetime
from pathlib import Path

from organizational_memory.analytics.reporting import generate_report
from organizational_memory.extraction.pipeline import ExtractionResult, run_extraction
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.json_store import JSONStore

NOW = datetime(2026, 3, 1, tzinfo=UTC)

MEETING_ONE = """# Sprint Planning

[10:00] Maria: We decided to adopt the new CI pipeline.
[10:02] Sam: I will own the migration to the new runners.
[10:05] Maria: The rollout is blocked by the staging outage.
TODO: update the deployment runbook.
"""

MEETING_TWO = """# Product Sync

[09:00] Aditya: We decided to ship the beta next week.
[09:02] Priya: I will prepare the release notes.
[09:05] Aditya: What is our rollback plan?
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

        print("1. Ingest + extract + persist")
        for text in (MEETING_ONE, MEETING_TWO):
            persist(store, run_extraction(text))
        print(f"   total records: {len(store.list_records())}")

        print("2. Recall")
        for query in ("ci pipeline", "beta", "release"):
            hits = search_keywords(store.list_records(), query)
            print(f"   recall {query!r:14} -> {len(hits)} hit(s)")

        print("3. Analytics")
        analytics = generate_report(store, now=NOW)
        print(f"   summary groups: {len(analytics.summary)}")

        print("4. Report")
        report = organizational_memory_report(store, now=NOW)
        print(f"   sections: {len(report.sections)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
