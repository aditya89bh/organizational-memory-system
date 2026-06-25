# API reference

This reference covers the public Python API of the organizational-memory
toolkit. Every function listed here is deterministic and runs locally with no
network access. For the command-line interface, see the
[user guide](user_guide.md).

All examples assume the package is installed (`pip install -e .`).

## Models

Domain models live in `organizational_memory.models`; their enums live in
`organizational_memory.models.enums`.

Core record types: `Decision`, `Task`, `Commitment`, `OpenLoop`, `Risk`,
`ActionItem`, `Dependency`, `Participant`, `Meeting`, `MemoryEvent`.

```python
from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.utils.time import utc_now

decision = Decision(
    id="d-1",
    title="Adopt weekly releases",
    description="Ship a release every Friday.",
    owner_id="alice",
    status=DecisionStatus.ACCEPTED,
    created_at=utc_now(),
    updated_at=utc_now(),
)
print(decision.to_dict())
```

Conversion helpers are in `organizational_memory.persistence`:

```python
from organizational_memory.persistence import to_dict, from_dict
from organizational_memory.models import Decision

data = to_dict(decision)
restored = from_dict(Decision, data)
```

## Extraction

`organizational_memory.extraction.pipeline.run_extraction` turns transcript text
into an `ExtractionResult`. Behavior is tuned with
`organizational_memory.extraction.config.ExtractionConfig`.

```python
from organizational_memory.extraction.pipeline import run_extraction

result = run_extraction(
    "Alice: We decided to launch on Friday.\n"
    "Bob: I will prepare the release notes."
)
print(len(result.decisions), len(result.commitments))
```

`ExtractionResult` exposes: `participants`, `decisions`, `commitments`, `tasks`,
`open_loops`, `risks`, `action_items`, `dependencies`, `topics`, `entities`,
`segments`, `speaker_turns`, and `traces`.

## Storage

`organizational_memory.storage.store.MemoryStore` is the abstract interface.
Two implementations are provided: `JSONStore` and `SQLiteStore`. Both take a
single path.

```python
from organizational_memory.storage.json_store import JSONStore

store = JSONStore("memory.json")
store.save_record(decision)
loaded = store.get_record("Decision", "d-1")
all_decisions = store.list_records("Decision")
```

Key methods: `save_record`, `get_record(record_type, record_id)`,
`list_records(record_type=None)`, `update_record`, `delete_record`, `query`, and
`clear`.

## Recall

`organizational_memory.recall.query_parser.parse_query` parses a compact query
into a `ParsedQuery`; `organizational_memory.recall.keyword_search.search_keywords`
performs lexical search over records.

```python
from organizational_memory.recall.query_parser import parse_query
from organizational_memory.recall.keyword_search import search_keywords

parsed = parse_query("owner:alice status:open release")
results = search_keywords(store.list_records(), "release")
```

Queries combine free text with `key:value` filters: `owner`, `status`, `type`,
`priority`, `severity`, `after`, `before`, and `meeting`.

## Analytics

`organizational_memory.analytics.reporting.generate_report` derives an
`AnalyticsReport` (summary metrics, memory health, bottlenecks, owner load) from
a store. Pass `now` for deterministic, time-relative metrics.

```python
from organizational_memory.analytics.reporting import generate_report
from organizational_memory.utils.time import parse_timestamp

report = generate_report(store, now=parse_timestamp("2026-03-01T00:00:00Z"))
print(report.summary)
```

## Reports

Report builders in `organizational_memory.reports` assemble typed `Report`
objects. For example,
`organizational_memory.reports.organizational_memory_report.organizational_memory_report`:

```python
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.reports.exporters.markdown import MarkdownExporter

report = organizational_memory_report(store)
markdown = MarkdownExporter().export(report)
```

Exporters live in `organizational_memory.reports.exporters`: `MarkdownExporter`,
`JSONExporter`, and `CSVExporter`. Each exposes `export(report) -> str`.

## CLI entry point

`organizational_memory.cli.main` exposes `build_parser()` and `main(argv)`.
`main` returns a process exit code.

```python
from organizational_memory.cli.main import main

exit_code = main(["recall", "release", "--store", "memory.json"])
```

The installed console script `organizational-memory` calls this same `main`.

## Observability and performance

- `organizational_memory.observability.structured_logging` — JSON-safe
  `LogEvent` and `StructuredLogger`.
- `organizational_memory.observability.error_reporting` — local `ErrorReport`
  via `build_error_report(error, component=...)`.
- `organizational_memory.performance.profiling` — `Profiler` with a `timer`
  context manager and a JSON-safe `ProfileReport`.
- `organizational_memory.config_validation` — `validate_*` helpers returning a
  `ValidationResult`.
