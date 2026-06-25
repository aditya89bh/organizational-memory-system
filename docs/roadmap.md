# Roadmap

This roadmap describes what is done, what remains, and what is intentionally out
of scope. The project is a local, deterministic organizational-memory toolkit
with no network calls and no external models.

## Completed phases

- **Phase 1 — Foundation & project setup.** Packaging, configuration,
  utilities, base schemas, tooling, and CI.
- **Phase 2 — Domain model.** Concrete schemas for meetings, decisions,
  commitments, tasks, open loops, and related records.
- **Phase 3 — Information extraction.** Deterministic, rule-based extraction of
  structured records from transcripts.
- **Phase 4 — Storage.** JSON and SQLite stores, repositories, queries,
  snapshots, and migrations.
- **Phase 5 — Recall & query engine.** Query parsing, lexical search, ranking,
  explanations, and pagination.
- **Phase 6 — Workflow intelligence & analytics.** Deterministic metrics,
  dashboards, and visualizations.
- **Phase 7 — Reports & organizational memory products.** Typed report model,
  report builders, and Markdown/JSON/CSV exporters.
- **Phase 8 — CLI, integrations & demos.** Command-line interface, example
  datasets, and reproducible demos.
- **Phase 9 — Production hardening.** Structured logging, local error reporting,
  configuration validation, coverage/benchmark/load/stress/fuzz tooling, package
  and release validation, and release documentation.

## Remaining work

### Phase 10 — Release & showcase (planned)

- Publish a versioned, installable artifact (wheel + source distribution).
- Tag a release and publish release notes derived from the changelog.
- Add a short showcase: recorded terminal walkthroughs (as text captures) and a
  curated example gallery built from the bundled datasets.
- Expand contributor onboarding and triage documentation.

## Future possible improvements

These are candidate ideas, not commitments. They would be evaluated against the
project's local-and-deterministic principles before any work began.

- Additional store backends behind the existing `MemoryStore` interface.
- Richer recall ranking signals while remaining fully lexical and deterministic.
- More report types and export formats.
- Optional, clearly-isolated integrations that a user explicitly opts into.

## Explicit non-goals

- **No network dependence.** The toolkit will not require network access to
  function.
- **No external models, embeddings, or hosted APIs** in the core toolkit.
- **No hidden telemetry** or background data collection.
- **No multi-tenant SaaS** behavior baked into the core library; any hosted
  offering would be a separate layer built on top.
- **No non-deterministic core behavior.** Given the same inputs, outputs must be
  reproducible.
