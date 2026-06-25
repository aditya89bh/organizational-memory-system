"""Tutorial 2: persist extracted memory and recall it.

Run it with::

    python examples/tutorials/tutorial_02_persist_and_recall.py

This tutorial extends tutorial 1: it extracts records, persists them in a local
JSON store (created in a temporary directory so nothing is left behind), and then
runs deterministic keyword recall over the stored memory. No network is used.
"""

import tempfile
from pathlib import Path

from organizational_memory.extraction.pipeline import ExtractionResult, run_extraction
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.json_store import JSONStore

TRANSCRIPT = """# Product Sync

[09:00] Aditya: We decided to ship the beta next week.
[09:02] Priya: I will prepare the release notes.
[09:04] Rahul: The release is blocked by the load test.
[09:05] Aditya: What is our rollback plan?
TODO: schedule the load test.
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


def persist(store: JSONStore, result: ExtractionResult) -> int:
    saved = 0
    for attr in _GROUPS:
        records: list[BaseRecord] = getattr(result, attr)
        for record in records:
            store.save_record(record)
            saved += 1
    return saved


def main() -> int:
    result = run_extraction(TRANSCRIPT)
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        saved = persist(store, result)
        print(f"Persisted {saved} records to a local JSON store.")

        for query in ("beta", "release", "load test"):
            hits = search_keywords(store.list_records(), query)
            print(f"  recall {query!r:14} -> {len(hits)} hit(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
