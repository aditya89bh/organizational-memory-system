# Persistence & Memory Store

The storage layer persists organizational memory records (decisions,
commitments, tasks, open loops, meetings, events, and more) behind a single
interface, so application code never depends on a particular backend.

## Architecture

```
records (Phase 2 models)
        │  encode_record / decode_record
        ▼
   MemoryStore  ◄── abstract interface
        ├── JSONStore     (single JSON file)
        └── SQLiteStore   (SQLite database)
        │
        ├── Repository[T] (typed view over one record type)
        ├── Query         (declarative filtering)
        ├── snapshot      (export / import)
        ├── backup        (timestamped snapshot rotation)
        └── migrations    (version upgrades for snapshots)
```

Every record is serialized with the Phase 2 persistence helpers, so all stores
share one on-disk representation and records can move freely between them.

## Stores

Both stores implement the same `MemoryStore` interface:

| Method | Description |
| --- | --- |
| `save_record(record)` | Insert or replace a record. |
| `get_record(type, id)` | Fetch one record, or `None`. |
| `list_records(type=None)` | List all records, optionally by type. |
| `update_record(record)` | Replace an existing record; raises `RecordNotFoundError` if absent. Touches `updated_at`. |
| `delete_record(type, id)` | Delete a record, returning whether it existed. |
| `remove_record(type, id)` | Delete, raising `RecordNotFoundError` if absent. |
| `clear()` | Remove all records. |
| `query(query)` | Filter / order / page records (see below). |
| `delete_where(query)` | Delete every record matching a query. |

### JSONStore

Stores everything in a single JSON file as `{type: {id: payload}}`. Output is
written with sorted keys and indentation, so files are deterministic and
diff-friendly. Best for small datasets, fixtures, and human inspection.

```python
from organizational_memory.storage import JSONStore
from organizational_memory.models import Decision

store = JSONStore("memory.json")
store.save_record(Decision(title="Adopt SQLite", description="use sqlite"))
```

### SQLiteStore

Stores records in a `records` table keyed by `(type, id)`, with `created_at` and
`updated_at` promoted to columns for efficient filtering. Supports use as a
context manager and persists across reopens. Best for larger datasets.

```python
from organizational_memory.storage import SQLiteStore

with SQLiteStore("memory.db") as store:
    store.save_record(decision)
```

## Repositories

`Repository[T]` is a typed view scoped to a single record type, returning the
concrete model instead of the base record:

```python
from organizational_memory.storage import DecisionRepository

decisions = DecisionRepository(store)
decisions.add(decision)
decisions.get(decision.id)        # -> Decision | None
decisions.list()                  # -> list[Decision]
decisions.update(decision)
decisions.remove(decision.id)     # raises if missing
```

Typed repositories ship for meetings, decisions, commitments, tasks, open
loops, and memory events.

## Querying

`Query` describes a declarative filter; all set criteria are combined with AND.
Results are ordered by `(created_at, id)` and support paging.

```python
from organizational_memory.storage import Query

store.query(Query(owner_id="alice"))
store.query(Query(record_type="Task", status="open"))
store.query(Query(text_contains="pricing"))
store.query(Query(created_after=start, created_before=end, limit=20, offset=40))
```

| Field | Matches |
| --- | --- |
| `record_type` | Records of that class. |
| `owner_id` | Records whose `owner_id` equals the value. |
| `status` | Records whose `status` value equals the string. |
| `source_meeting_id` | Records linked to that meeting. |
| `text_contains` | Case-insensitive substring of title/description/etc. |
| `created_after` / `created_before` | Inclusive `created_at` bounds. |
| `limit` / `offset` | Pagination. |

## Indexes

`build_indexes(records)` produces deterministic, in-memory `RecordIndexes`
mapping values to record ids by type, owner, meeting, status, and date. They are
read-only lookups, not persisted.

## Snapshots

A snapshot is a self-contained, JSON-serializable dump of an entire store. Use
it for exports, fixtures, or moving data between store backends.

```python
from organizational_memory.storage import create_snapshot, restore_snapshot

snapshot = create_snapshot(source_store)
restore_snapshot(target_store, snapshot)        # clears target first
restore_snapshot(target_store, snapshot, replace=False)  # merge
```

`write_snapshot(store, path)` and `read_snapshot(path)` persist a snapshot to
disk.

## Backups

Backups are timestamped snapshot files with simple rotation:

```python
from organizational_memory.storage import (
    backup_store, list_backups, restore_latest, prune_backups,
)

backup_store(store, "backups/")     # writes snapshot-<timestamp>.json
list_backups("backups/")            # oldest -> newest
restore_latest(store, "backups/")   # restore newest backup
prune_backups("backups/", keep=5)   # delete all but the 5 newest
```

## Migrations

Snapshots carry a `version`. When the on-disk shape changes, register a
`Migration` describing how to upgrade one version to the next; `migrate_snapshot`
chains the registered steps up to `LATEST_VERSION`. `restore_snapshot` migrates
older snapshots automatically (pass `migrate=False` to opt out).

## Benchmarks

`scripts/run_storage_benchmarks.py` times save/get/list/query across both stores
for a configurable record count:

```bash
python scripts/run_storage_benchmarks.py
```
