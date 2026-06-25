"""Runnable natural-language recall example.

Run it with::

    python examples/recall/natural_language_recall_example.py

Answers a few conservative, deterministic natural-language questions against a
temporary store. No LLMs or network calls are involved. Nothing is left on disk.
"""

import tempfile
from datetime import timedelta
from pathlib import Path

from organizational_memory.models import Commitment, Decision, OpenLoop, Task
from organizational_memory.models.enums import OpenLoopStatus
from organizational_memory.recall.natural_language import answer
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def main() -> int:
    now = utc_now()
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        store.save_record(
            Decision(
                id="d1",
                title="Choose Postgres",
                description="use postgres for pricing",
            )
        )
        store.save_record(
            Task(
                id="t1",
                title="Launch landing page",
                description="ship it",
                owner_id="alice",
            )
        )
        store.save_record(
            OpenLoop(id="o1", question="auth approach?", status=OpenLoopStatus.OPEN)
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

        questions = [
            "What decisions were made about pricing?",
            "Who owns the launch task?",
            "What is still unresolved?",
            "What is overdue?",
        ]
        for question in questions:
            results = answer(store, question, now=now)
            ids = [result.record.id for result in results]
            print(f"{question} -> {ids}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
