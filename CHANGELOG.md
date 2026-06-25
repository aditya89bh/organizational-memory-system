# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This is a local, deterministic organizational-memory toolkit. It performs no
network calls and uses no external models or APIs.

## [Unreleased]

No unreleased changes. The current line is the v0.1.0 release described below.

## [0.1.0] - 2026-06-25

First tagged release. A complete local, deterministic organizational-memory
toolkit. No network calls, no external models or embeddings.

### Added

- **Models.** Typed domain records for meetings, participants, decisions,
  commitments, tasks, open loops, dependencies, risks, action items, topics, and
  memory events, sharing a common base record with serialization helpers.
- **Extraction.** Deterministic, rule-based extraction pipeline producing typed
  records with confidence scores and audit traces.
- **Storage.** `MemoryStore` interface with interchangeable JSON and SQLite
  backends, repositories, queries, indexes, snapshots, backups, and migrations.
- **Recall.** Compact query parser and lexical keyword search with coverage
  scoring, an exact-phrase bonus, ranking, explanations, traces, and pagination.
- **Analytics.** Memory health, bottlenecks, ownership load, decision velocity,
  commitment completion, open-loop aging, overdue work, productivity, and
  dashboards.
- **Reports.** Typed report model with meeting, weekly, monthly, decision,
  commitment, open-loop, follow-up, and organizational-memory reports, plus
  Markdown/JSON/CSV exporters.
- **CLI & demos.** The `organizational-memory` command-line interface (ingest,
  recall, report, analytics, commitments, open-loops, export, config, demo,
  benchmark), bundled datasets, and reproducible demos.
- **Hardening.** Structured logging, local error reporting, configuration
  validation, profiling utilities, and coverage/benchmark/load/stress/fuzz
  tooling.
- **Release & showcase.** Repository walkthrough, case studies, tutorials,
  examples gallery, documentation index, benchmark visualizations, release notes,
  release checklist, release validation and post-release verification scripts.

### Notes

- Lexical recall only; no semantic search, embeddings, or external model APIs.
- Local-only: no server, authentication, or multi-user isolation.

## Phase summary

The project was built in phases. Each phase added one cohesive capability set.

- **Phase 1 — Foundation & project setup.** Package layout, tooling (ruff,
  mypy, pytest), constants, logging utilities, core helpers.
- **Phase 2 — Organizational memory models.** Typed domain models for
  decisions, tasks, commitments, open loops, meetings, participants, risks,
  action items, dependencies, and events.
- **Phase 3 — Information extraction engine.** Deterministic, rule-based
  extractors and the extraction pipeline with normalization and confidence
  filtering.
- **Phase 4 — Memory store & persistence.** `MemoryStore` interface with JSON
  and SQLite implementations, encoding/decoding, snapshots, and migrations.
- **Phase 5 — Recall & query engine.** Query parser and lexical keyword search
  with scoring and filtering.
- **Phase 6 — Workflow intelligence & analytics.** Analytics for memory health,
  bottlenecks, ownership load, decision velocity, and commitment completion.
- **Phase 7 — Reports & organizational memory products.** Typed report model,
  multiple report builders, and Markdown/JSON/CSV exporters.
- **Phase 8 — CLI, integrations & demos.** `argparse`-based CLI, runnable demos,
  example datasets, and user-facing documentation.
- **Phase 9 — Production hardening.** Observability, configuration validation,
  benchmarking, expanded testing, and release documentation.
- **Phase 10 — Release & showcase.** Walkthrough, case studies, tutorials,
  documentation index, benchmark visualizations, release notes/checklist,
  release validation, and the v0.1.0 release.

## Current version notes

- Version: `0.1.0`.
- Runtime requirements: Python >= 3.11, standard library only at runtime.
- The CLI entry point is `organizational-memory`
  (`organizational_memory.cli.main:main`).

## Migration notes

- v0.1.0 is the first tagged release, so there are no upgrade migrations from a
  prior released version.
- Store files written during development remain compatible; the JSON and SQLite
  store formats and snapshot/migration helpers introduced in Phase 4 are
  unchanged.
