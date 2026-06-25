# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This is a local, deterministic organizational-memory toolkit. It performs no
network calls and uses no external models or APIs.

## [Unreleased]

The current development line is the Phase 9 production-hardening work described
below. No public package release has been published yet; the in-repo version is
`0.1.0`.

### Added

- Structured logging with JSON-safe log events.
- Local, deterministic error reporting (no external service).
- Configuration validation for store paths/types, CLI config files, extractor
  names, report/export formats, and benchmark types.
- Coverage reporting configuration and a deterministic coverage gate script.
- Performance, memory, load, and stress benchmark scripts.
- Profiling utilities (timer context manager and aggregate profile report).
- Pseudo-fuzz tests, broader edge-case tests, package verification, and release
  validation tests.
- Security, architecture, API, roadmap, production-readiness, and deployment
  documentation; updated contribution guide.

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
  benchmarking, expanded testing, and release documentation (this phase).

## Current version notes

- Version: `0.1.0` (pre-release, in active development).
- Runtime requirements: Python >= 3.11, standard library only at runtime.
- The CLI entry point is `organizational-memory`
  (`organizational_memory.cli.main:main`).

## Migration notes

- No public releases have been made, so there are no upgrade migrations between
  released versions yet.
- Store files written by earlier phases remain compatible; the JSON and SQLite
  store formats and snapshot/migration helpers introduced in Phase 4 are
  unchanged by Phase 9.
