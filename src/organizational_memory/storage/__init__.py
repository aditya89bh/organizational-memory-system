"""Persistence layer for organizational memory records."""

from organizational_memory.storage.backup import (
    backup_store,
    latest_backup,
    list_backups,
    prune_backups,
    restore_latest,
)
from organizational_memory.storage.commitment_repository import (
    CommitmentRepository,
)
from organizational_memory.storage.decision_repository import DecisionRepository
from organizational_memory.storage.event_repository import EventRepository
from organizational_memory.storage.indexes import RecordIndexes, build_indexes
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.meeting_repository import MeetingRepository
from organizational_memory.storage.migrations import (
    LATEST_VERSION,
    Migration,
    MigrationError,
    migrate_snapshot,
)
from organizational_memory.storage.open_loop_repository import OpenLoopRepository
from organizational_memory.storage.query import Query, apply_query, matches
from organizational_memory.storage.repository import Repository
from organizational_memory.storage.snapshot import (
    create_snapshot,
    read_snapshot,
    restore_snapshot,
    write_snapshot,
)
from organizational_memory.storage.sqlite_store import SQLiteStore
from organizational_memory.storage.store import (
    RECORD_TYPES,
    MemoryStore,
    RecordNotFoundError,
    decode_record,
    encode_record,
    record_type_name,
    resolve_record_type,
)
from organizational_memory.storage.task_repository import TaskRepository

__all__ = [
    "LATEST_VERSION",
    "RECORD_TYPES",
    "CommitmentRepository",
    "DecisionRepository",
    "EventRepository",
    "JSONStore",
    "MeetingRepository",
    "MemoryStore",
    "Migration",
    "MigrationError",
    "OpenLoopRepository",
    "Query",
    "RecordIndexes",
    "RecordNotFoundError",
    "Repository",
    "SQLiteStore",
    "TaskRepository",
    "apply_query",
    "backup_store",
    "build_indexes",
    "create_snapshot",
    "decode_record",
    "encode_record",
    "latest_backup",
    "list_backups",
    "matches",
    "migrate_snapshot",
    "prune_backups",
    "read_snapshot",
    "record_type_name",
    "resolve_record_type",
    "restore_latest",
    "restore_snapshot",
    "write_snapshot",
]
