# Feature summary — v0.1.0

A local, deterministic toolkit that turns meeting text into structured
organizational memory. No network calls, no external models or embeddings.

## Implemented

- **Ingestion & extraction** — rule-based, deterministic extraction of decisions,
  commitments, tasks, open loops, participants, risks, action items,
  dependencies, and topics from text and Markdown transcripts.
- **Storage** — `MemoryStore` interface with interchangeable JSON and SQLite
  backends, repositories, queries, indexes, snapshots, backups, and migrations.
- **Recall** — compact query parser (`key:value` + free text) and lexical
  keyword search with coverage scoring and an exact-phrase bonus.
- **Analytics** — memory health, bottlenecks, owner load, decision velocity,
  commitment completion, open-loop aging, overdue work, productivity, dashboards.
- **Reports** — typed report builders with Markdown/JSON/CSV exporters.
- **CLI** — `organizational-memory` with ten subcommands.
- **Demos & tutorials** — reproducible end-to-end demos and step-by-step
  tutorial scripts.
- **Hardening** — structured logging, local error reporting, configuration
  validation, profiling, and coverage/benchmark/load/stress/fuzz tooling.

## Not included (future work)

- No hosted service, server, authentication, or multi-user isolation.
- No LLMs, embeddings, or external model APIs.
- No semantic search (recall is lexical).
- No encryption of store files at rest.

See [docs/roadmap.md](../docs/roadmap.md) for the full roadmap and non-goals.
