# Repository walkthrough

This walkthrough orients a new reader: what the project does, why it exists, how
it is structured, how to run it, and how to navigate the codebase. It is a local,
deterministic organizational-memory toolkit — no network calls, no external
models, no embeddings.

## What the project does

The toolkit turns unstructured meeting text into structured organizational
memory. Given a transcript, it deterministically extracts:

- **decisions** (what was decided, by whom, with rationale),
- **commitments** (who promised what, and by when),
- **tasks** (work items derived from the conversation),
- **open loops** (unresolved questions),

plus participants, risks, action items, dependencies, and topics. Those records
are persisted to a local store and can be recalled, analyzed, and reported on.

## Why it exists

Organizations forget. Decisions get re-litigated, commitments slip, and the same
questions resurface months later. Most knowledge lives in documents that are easy
to write but hard to recall. This project treats organizational memory as a
first-class, structured, queryable asset.

## How the system is structured

The pipeline is a sequence of small, composable layers:

```
transcript -> ingestion -> extraction -> memory store
                                              |
                       +----------------------+----------------------+
                       v                                             v
                    recall                                   analytics + reports
                       |                                             |
                       +---------------------+-----------------------+
                                             v
                                            CLI
```

See [architecture.md](architecture.md) for detailed text diagrams of each layer.

## How to run the CLI

Install the package and use the `organizational-memory` console script:

```bash
pip install -e .
organizational-memory --help
organizational-memory ingest meeting.txt --store memory.json --backend json
organizational-memory recall "release" --store memory.json --backend json
organizational-memory report weekly --store memory.json --now 2026-03-01T00:00:00Z
```

Full command coverage is in the [user guide](user_guide.md) and the
[interactive walkthrough](interactive_walkthrough.md).

## How to run the demos

The toolkit ships reproducible, deterministic demos:

```bash
organizational-memory demo --list
organizational-memory demo startup
organizational-memory demo all
```

Each demo is described in [demos.md](demos.md).

## How to understand the codebase

The package lives under `src/organizational_memory/`:

| Area | Module | Responsibility |
| --- | --- | --- |
| Ingestion | `ingestion/` | Load and normalize transcript text. |
| Extraction | `extraction/` | Rule-based extractors and the pipeline. |
| Models | `models/`, `schemas/` | Typed domain records and base record. |
| Storage | `storage/` | `MemoryStore` interface, JSON and SQLite stores. |
| Recall | `recall/` | Query parsing and lexical keyword search. |
| Analytics | `analytics/` | Metrics, dashboards, and health scoring. |
| Reports | `reports/` | Report builders and Markdown/JSON/CSV exporters. |
| CLI | `cli/` | `argparse` entry point and subcommands. |
| Observability | `observability/` | Structured logging and local error reports. |
| Performance | `performance/` | Profiling utilities. |
| Demos | `demos/` | Deterministic end-to-end demonstrations. |

Tests live in `tests/`, runnable examples in `examples/`, helper scripts in
`scripts/`, and documentation in `docs/`.

## How the phases map to the repo

The project was built in ten phases, each adding one cohesive capability set:

1. **Foundation** — packaging, tooling, base schemas (`pyproject.toml`, `utils/`).
2. **Domain model** — typed records (`models/`, `schemas/`).
3. **Extraction** — rule-based extraction (`extraction/`).
4. **Storage** — JSON and SQLite stores (`storage/`).
5. **Recall** — query parser and search (`recall/`).
6. **Analytics** — metrics and dashboards (`analytics/`).
7. **Reports** — report builders and exporters (`reports/`).
8. **CLI & demos** — command-line interface and demos (`cli/`, `demos/`).
9. **Production hardening** — observability, validation, benchmarks, tests.
10. **Release & showcase** — documentation, case studies, and release artifacts.

For the full history see the [changelog](../CHANGELOG.md) and the
[roadmap](roadmap.md).
