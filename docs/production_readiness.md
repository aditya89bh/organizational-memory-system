# Production readiness

This guide states honestly what is ready, what is local-only, and what would
need to change before the toolkit could back a hosted, multi-user service. The
project is a **local, deterministic** organizational-memory toolkit.

## What is ready

- **Deterministic core.** Extraction, recall, analytics, and reporting are
  rule-based and reproducible: the same input always yields the same output.
- **Typed, tested codebase.** Fully type-annotated, checked with `mypy --strict`,
  linted with `ruff`, and covered by a deterministic `pytest` suite.
- **Two storage backends.** JSON and SQLite stores behind a common
  `MemoryStore` interface.
- **Command-line interface.** A complete local CLI for ingest, recall, report,
  analytics, commitments, open loops, export, config, demo, and benchmark.
- **Observability primitives.** Structured logging and local error reporting,
  both JSON-safe and in-process.
- **Validation tooling.** Configuration validation, package verification, and
  release validation tests.
- **Benchmark tooling.** Performance, memory, load, and stress scripts that
  report counts and elapsed time without fragile thresholds.

## What is local-only

- The toolkit runs on a single machine against local files.
- There is **no server, API, authentication, or authorization** layer.
- There is **no network access** of any kind at runtime.
- Stores are **plaintext on disk** and are not encrypted by the toolkit.

## Limitations

- No concurrency control for simultaneous writers to the same store file.
- No built-in resource quotas; very large inputs consume proportional CPU and
  memory.
- No multi-user isolation, roles, or access control.
- No background processing, scheduling, or daemon mode.

## Operational checklist

Before relying on the toolkit locally:

- [ ] Install with a pinned Python (>= 3.11) in an isolated virtual environment.
- [ ] Choose a store backend and a stable path you control.
- [ ] Back up store files as part of your normal file backups.
- [ ] Run `ruff check .`, `mypy .`, and `pytest` after any local changes.
- [ ] Run `python scripts/verify_package.py` to confirm package integrity.
- [ ] Restrict filesystem permissions on store files and exports.

## Testing posture

- Deterministic unit tests, edge-case tests, pseudo-fuzz tests (fixed seeds),
  and release validation tests.
- Coverage is opt-in via `pytest --cov`; a coverage gate script is provided.
- Benchmarks are informational and do not assert hard timing thresholds.

See [docs/testing.md](testing.md).

## Security posture

- No network calls, no external models, no secret management.
- Inputs are assumed to come from a trusted operator.
- Plaintext storage; protect with filesystem permissions and disk encryption.

See [docs/security.md](security.md).

## Scaling considerations

- The JSON store rewrites the whole file on each mutation; for large datasets the
  SQLite store is the better choice.
- Recall and analytics operate in memory over loaded records; very large stores
  will increase memory use proportionally.
- There is no sharding, replication, or distributed coordination.

## Future work before SaaS deployment

A hosted, multi-user deployment is **out of scope** for the core toolkit and
would require a separate layer providing, at minimum:

- Authentication, authorization, and per-tenant isolation.
- A service API and persistent, concurrent-safe storage.
- Encryption at rest and in transit.
- Operational monitoring, alerting, rate limiting, and quotas.
- A formal data-retention and privacy policy.

See the [roadmap](roadmap.md) for planned, in-scope work.
