# Organizational Memory System

> Convert meetings, conversations, and notes into structured organizational
> memory consisting of decisions, commitments, tasks, and open loops.

## Overview

The Organizational Memory System ingests the unstructured records an
organization produces every day — meeting transcripts, chat threads, and notes —
and turns them into a queryable, structured memory. Instead of losing context in
scattered documents, teams capture *what was decided*, *who committed to what*,
*which tasks exist*, and *which questions remain open*.

## Motivation

Organizations forget. Decisions get re-litigated, commitments slip through the
cracks, and the same questions resurface months later. Most knowledge lives in
documents that are easy to write but hard to recall. This project treats
organizational memory as a first-class, structured asset that can be ingested,
stored, recalled, and reported on.

## Architecture vision

The system is built from small, composable modules:

- **Ingestion** — read supported source files and normalize them into raw input.
- **Extraction** — deterministically extract structured records from transcripts.
- **Schemas** — typed records for decisions, commitments, tasks, and open loops,
  all sharing a common base record (identity + timestamps + serialization).
- **Storage** — persist and retrieve structured memory records.
- **Recall & reporting** — answer questions about the memory and produce digests.

This repository currently provides the foundation: configuration, environment
loading, logging, an exception hierarchy, shared utilities (identifiers,
timestamps, serialization), and the base record schema.

## Planned features

- Ingest meetings, conversations, and notes from multiple file formats.
- Extract and store decisions with rationale and context.
- Track commitments and their owners.
- Track tasks derived from conversations.
- Track unresolved questions as open loops.
- Recall and report across the accumulated organizational memory.

## Installation

Requires Python 3.11 or newer.

```bash
pip install -e .
```

For a development setup with linting, type checking, and tests:

```bash
pip install -e ".[dev]"
```

## Development

Run the full quality gate locally:

```bash
ruff check .
mypy .
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete workflow and commit
conventions.

## Domain models

The core domain models live in `organizational_memory.models` and represent
meetings, participants, decisions, commitments, tasks, open loops, dependencies,
risks, discussion topics, action items, and memory events. They are supported by
string-valued status enumerations, ownership and audit metadata, relationship
schemas, a timeline, and `persistence` helpers (`to_dict` / `from_dict`) for
JSON-compatible conversion.

See [docs/schemas.md](docs/schemas.md) for the full schema reference and example
JSON objects.

## Extraction

The `organizational_memory.extraction` package converts raw text and markdown
transcripts into structured records using **deterministic, rule-based
heuristics** — no LLMs, no external APIs, and no network calls. It parses
speakers, segments the meeting, and extracts decisions, commitments, tasks,
open loops, dependencies, risks, action items, participants, and topics, each
annotated with a deterministic confidence score and an audit trace.

```python
from organizational_memory.extraction import run_extraction

result = run_extraction("Aditya: We decided to ship on Friday.")
print(result.decisions[0].title)
```

See [docs/extraction.md](docs/extraction.md) for the full extraction reference,
configuration options, and known limitations.

## Persistence

The `organizational_memory.storage` package persists records behind a single
`MemoryStore` interface, with interchangeable **JSON** and **SQLite** backends.
It provides typed repositories per record type, a declarative `Query` API,
in-memory indexes, snapshots, timestamped backups, and version-aware
migrations.

```python
from organizational_memory.storage import SQLiteStore, Query, DecisionRepository

with SQLiteStore("memory.db") as store:
    decisions = DecisionRepository(store)
    decisions.add(decision)
    open_for_alice = store.query(Query(owner_id="alice", status="open"))
```

See [docs/persistence.md](docs/persistence.md) for the full storage reference,
including snapshots, backups, and migrations.

## Recall

The `organizational_memory.recall` package retrieves records from the stores
using **deterministic search and ranking** — no embeddings, LLMs, external APIs,
or network calls. It provides keyword and per-record-type search, timeline and
relationship search, recency/importance/ownership/composite ranking, explainable
results, recall traces, pagination, a compact query parser, and conservative
natural-language-like recall.

```python
from organizational_memory.recall import answer, parse_query, search_keywords

results = answer(store, "What is still unresolved?")
parsed = parse_query("type:decision owner:alice kubernetes")
```

See [docs/recall.md](docs/recall.md) for the full recall reference, including the
query parser, ranking, explanations, traces, and limitations.

## Recall evaluation

Recall quality is measured deterministically against a fixed fixture dataset.
The benchmark harness in
[`scripts/run_recall_benchmarks.py`](scripts/run_recall_benchmarks.py) runs a set
of representative queries and reports hit rate and top-k accuracy, while
`organizational_memory.recall.metrics` provides reusable metrics (hit rate,
top-k hit rate, mean reciprocal rank, zero-result rate, average result count).

```bash
python scripts/run_recall_benchmarks.py
```

See [docs/recall_evaluation.md](docs/recall_evaluation.md) for the benchmark
design, metrics, fixture expectations, sample output, and limitations.

## Analytics metrics

The `organizational_memory.analytics` package turns persisted memory into
**deterministic** workflow metrics — no LLMs, embeddings, external APIs, or
network calls. It covers decision velocity, commitment completion, open loop
aging, overdue work, ownership load, meeting effectiveness, repeated
discussions, dependencies and bottlenecks, accountability, trends, timeline
activity, productivity, and an overall memory health score.

```python
from organizational_memory.analytics import generate_report, memory_health

report = generate_report(store)
health = memory_health(store)
print(health.score, health.grade)
```

See [docs/analytics_metrics.md](docs/analytics_metrics.md) for each metric, its
formula, inputs, limitations, and example output.

## Workflow intelligence

Phase 6 layers workflow intelligence over the stored memory: composite
**bottleneck** detection (overloaded owners, recurring unresolved topics, blocked
records, low-signal meetings), **accountability** scoring, **repeated discussion**
detection, an overall **memory health** score with recommendations, structured
**reports**, JSON-safe **dashboard snapshots**, and text-only **visualizations**.
It remains fully deterministic and makes no predictive claims.

```python
from organizational_memory.analytics import bottlenecks, build_dashboard_snapshot

snapshot = build_dashboard_snapshot(store)
hotspots = bottlenecks(store)
```

See [docs/workflow_intelligence.md](docs/workflow_intelligence.md) for the
analytics architecture, how analytics use memory records, and the full set of
limitations.

## Reporting

Phase 7 turns persisted memory, recall results, and analytics into deterministic
local reports: meeting summaries, decision/commitment/open-loop reports, weekly
and monthly reports, timeline, participant, accountability, organizational
memory, and follow-up reports. Reports share a common section/table model and can
be exported to Markdown, JSON, and CSV. Reusable templates and text-only
visualizations are included. Reports are reproducible from explicit inputs and
make no predictive or business-intelligence claims.

```python
from organizational_memory.reports import weekly_report
from organizational_memory.reports.exporters.markdown import MarkdownExporter

report = weekly_report(store, start=start, end=end)
markdown = MarkdownExporter().export(report)
```

See [docs/reporting_walkthrough.md](docs/reporting_walkthrough.md) for how to
generate each report, export to Markdown/JSON/CSV, and the limitations. Sample
outputs live under [docs/assets/](docs/assets/).

## Demos

The project ships with deterministic, runnable demos that exercise the full
pipeline end to end (extraction → persistence → recall → analytics → reports),
entirely in memory and with no external dependencies.

```bash
organizational-memory demo startup
organizational-memory demo all
```

```python
from organizational_memory.demos import run_demo

lines = run_demo("company-memory")
```

See [docs/demos.md](docs/demos.md) for each demo, the bundled example datasets,
expected outputs, and limitations.

## Roadmap

- **Phase 1 — Foundation & project setup**: packaging, configuration,
  utilities, base schemas, tooling, and CI.
- **Phase 2 — Domain model**: concrete schemas for meetings, decisions,
  commitments, tasks, open loops, and related records.
- **Phase 3 — Information extraction**: deterministic, rule-based
  extraction of structured records from transcripts and notes.
- **Phase 4 — Storage**: persist and retrieve structured records via
  JSON and SQLite stores, repositories, queries, snapshots, and backups.
- **Phase 5 — Recall & query engine**: deterministic search,
  ranking, explanations, traces, pagination, query parsing, and
  natural-language-like recall over the stored memory.
- **Phase 6 — Workflow intelligence & analytics**: deterministic
  metrics for decision velocity, commitment completion, open loop aging, overdue
  work, ownership, meeting effectiveness, repeated discussions, dependencies,
  bottlenecks, accountability, trends, timeline activity, productivity, and an
  overall memory health score, with reports, dashboards, and visualizations.
- **Phase 7 — Reports & organizational memory products** *(current)*:
  deterministic report generation (meeting, decision, commitment, open-loop,
  weekly, monthly, timeline, participant, accountability, organizational memory,
  and follow-up reports), Markdown/JSON/CSV exporters, reusable templates, and
  text-only report visualizations.

## License

Released under the [MIT License](LICENSE).
