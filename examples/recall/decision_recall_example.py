"""Runnable decision recall example.

Run it with::

    python examples/recall/decision_recall_example.py

Stores a few decisions and recalls them by text, owner, and status, printing the
matches. Nothing is left on disk.
"""

import tempfile
from pathlib import Path

from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.recall.decision_search import search_decisions
from organizational_memory.storage.json_store import JSONStore


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        store.save_record(
            Decision(
                id="d1",
                title="Adopt Kubernetes",
                description="run on kubernetes",
                owner_id="alice",
                status=DecisionStatus.ACCEPTED,
                rationale="scales better",
            )
        )
        store.save_record(
            Decision(
                id="d2",
                title="Pricing model",
                description="revisit pricing",
                owner_id="bob",
                status=DecisionStatus.PROPOSED,
            )
        )

        print("Decisions mentioning 'kubernetes':")
        for result in search_decisions(store, text="kubernetes"):
            assert isinstance(result.record, Decision)
            print(f"  - {result.record.id}: {result.record.title}")

        print("\nAccepted decisions:")
        for result in search_decisions(store, status=DecisionStatus.ACCEPTED):
            assert isinstance(result.record, Decision)
            print(f"  - {result.record.id}: {result.record.title}")

        print("\nDecisions owned by bob:")
        for result in search_decisions(store, owner_id="bob"):
            assert isinstance(result.record, Decision)
            print(f"  - {result.record.id}: {result.record.title}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
