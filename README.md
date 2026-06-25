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

## Roadmap

- **Phase 1 — Foundation & project setup**: packaging, configuration,
  utilities, base schemas, tooling, and CI.
- **Phase 2 — Domain model**: concrete schemas for meetings, decisions,
  commitments, tasks, open loops, and related records.
- **Phase 3 — Information extraction** *(current)*: deterministic, rule-based
  extraction of structured records from transcripts and notes.
- **Phase 4 — Storage**: persist and retrieve structured records.
- **Phase 5 — Recall & reporting**: query the memory and generate reports.

## License

Released under the [MIT License](LICENSE).
