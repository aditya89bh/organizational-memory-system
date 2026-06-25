"""Runnable demonstration of the storage layer.

Run it with::

    python examples/storage_demo.py

It creates an in-memory-style SQLite store in a temporary directory, populates a
few records through typed repositories, runs queries, takes a snapshot, makes a
backup, and prints what it finds. Nothing is left on disk.
"""

import tempfile
from pathlib import Path

from organizational_memory.models import Commitment, Decision, Meeting, Task
from organizational_memory.storage import (
    CommitmentRepository,
    DecisionRepository,
    MeetingRepository,
    Query,
    SQLiteStore,
    backup_store,
    build_indexes,
    create_snapshot,
)
from organizational_memory.utils.time import utc_now


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        store = SQLiteStore(root / "memory.db")

        meetings = MeetingRepository(store)
        decisions = DecisionRepository(store)
        commitments = CommitmentRepository(store)

        meeting = meetings.add(Meeting(title="Q3 Kickoff", started_at=utc_now()))
        decisions.add(
            Decision(
                title="Adopt SQLite for storage",
                description="Use the bundled SQLite store for persistence.",
                owner_id="alice",
                source_meeting_id=meeting.id,
            )
        )
        commitments.add(
            Commitment(
                owner_id="bob",
                description="Write the storage migration guide.",
                source_meeting_id=meeting.id,
            )
        )
        store.save_record(
            Task(
                title="Draft API docs",
                description="Outline endpoints",
                owner_id="alice",
            )
        )

        print("All records:")
        for record in store.list_records():
            print(f"  - {type(record).__name__}: {record.id}")

        print("\nRecords owned by alice:")
        for record in store.query(Query(owner_id="alice")):
            print(f"  - {type(record).__name__}: {record.id}")

        indexes = build_indexes(store.list_records())
        print("\nCounts by type:")
        for type_name, ids in indexes.by_type.items():
            print(f"  - {type_name}: {len(ids)}")

        snapshot = create_snapshot(store)
        total = sum(len(v) for v in snapshot["records"].values())
        print(f"\nSnapshot captured {total} records")

        backup = backup_store(store, root / "backups")
        print(f"Backup written to {backup.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
