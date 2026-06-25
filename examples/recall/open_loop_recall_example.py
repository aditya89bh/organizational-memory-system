"""Runnable open loop recall example.

Run it with::

    python examples/recall/open_loop_recall_example.py

Stores open loops and recalls the unresolved ones, printing the questions that
still need answers. Nothing is left on disk.
"""

import tempfile
from pathlib import Path

from organizational_memory.models import OpenLoop
from organizational_memory.models.enums import OpenLoopStatus
from organizational_memory.recall.open_loop_search import search_open_loops
from organizational_memory.storage.json_store import JSONStore


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        store.save_record(
            OpenLoop(
                id="o1",
                question="How do we handle authentication?",
                owner_id="alice",
                status=OpenLoopStatus.OPEN,
            )
        )
        store.save_record(
            OpenLoop(
                id="o2",
                question="Which database did we pick?",
                status=OpenLoopStatus.RESOLVED,
            )
        )

        print("Unresolved open loops:")
        for result in search_open_loops(store, status=OpenLoopStatus.OPEN):
            assert isinstance(result.record, OpenLoop)
            print(f"  - {result.record.id}: {result.record.question}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
