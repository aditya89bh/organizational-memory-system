"""Runnable keyword search example.

Run it with::

    python examples/recall/keyword_search_example.py

Populates a temporary store and runs a deterministic keyword search, printing the
matched records with their scores and matched tokens. Nothing is left on disk.
"""

import tempfile
from pathlib import Path

from organizational_memory.models import Decision, Task
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.storage.json_store import JSONStore


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        store.save_record(
            Decision(
                id="d1",
                title="Adopt Kubernetes",
                description="run services on kubernetes",
            )
        )
        store.save_record(
            Decision(id="d2", title="Pricing model", description="revisit pricing")
        )
        store.save_record(
            Task(
                id="t1",
                title="Migrate cluster to kubernetes",
                description="ops",
                owner_id="alice",
            )
        )

        print("Keyword search for 'kubernetes':")
        for result in search_keywords(store.list_records(), "kubernetes"):
            tokens = result.details["matched_tokens"]
            print(
                f"  - {type(result.record).__name__} {result.record.id} "
                f"score={result.score} tokens={tokens}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
