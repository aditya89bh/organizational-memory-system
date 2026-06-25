# User guide

This guide covers everyday use of the `organizational-memory` command-line
interface. The CLI is local and deterministic: it uses no LLMs, embeddings,
external APIs, or network calls.

## Installation

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the `organizational-memory` console script. Confirm it works:

```bash
organizational-memory --version
organizational-memory --help
```

## CLI commands

| Command | Purpose |
| --- | --- |
| `ingest <path>` | Extract a transcript/notes file and persist the memory. |
| `recall "<query>"` | Search memory with keywords and `key:value` filters. |
| `report <type>` | Generate a report as Markdown or JSON. |
| `analytics` | Show summary metrics, memory health, bottlenecks, owner load. |
| `commitments` | List and filter commitments. |
| `open-loops` | List and filter open loops. |
| `export <format>` | Export a memory snapshot or report as json/markdown/csv. |
| `config <action>` | Show, initialize, validate, or update local configuration. |
| `demo <name>` | Run a bundled, deterministic demo. |
| `benchmark <type>` | Run deterministic benchmarks. |

Every command supports `--help`.

## Stores

Records are persisted behind a single store interface with two backends:

- **JSON** (`--backend json`, default): a single deterministic JSON file.
- **SQLite** (`--backend sqlite`): a local SQLite database file.

Select the store path and backend on any command:

```bash
organizational-memory analytics --store memory.json --backend json
organizational-memory analytics --store memory.db --backend sqlite
```

## Ingesting files

Ingest a `.txt` transcript or `.md` notes file. Optionally attach a meeting
record so reports can be scoped to that meeting:

```bash
organizational-memory ingest meeting.txt --store memory.json --meeting-id sync-1
```

The command prints an extraction summary with counts per record type.

## Recalling memory

```bash
organizational-memory recall "launch" --store memory.json
organizational-memory recall "type:decision owner:alice pricing" \
  --store memory.json --limit 5 --offset 0 --explain
```

- `key:value` filters: `type`, `owner`, `status`, `priority`, `severity`,
  `after`, `before`, `meeting`.
- `--explain` prints why each result matched and how it was scored.

## Analytics

```bash
organizational-memory analytics --store memory.json --now 2026-03-01T00:00:00Z
organizational-memory analytics --store memory.json --format json \
  --now 2026-03-01T00:00:00Z
```

Pass `--now` for reproducible output.

## Reports

Supported types: `meeting`, `weekly`, `follow-up`, `organizational-memory`,
`decisions`, `commitments`, `open-loops`.

```bash
organizational-memory report follow-up --store memory.json --now 2026-03-01T00:00:00Z
organizational-memory report meeting --store memory.json --meeting-id sync-1 \
  --now 2026-03-01T00:00:00Z
organizational-memory report weekly --store memory.json \
  --start 2026-02-22T00:00:00Z --end 2026-03-01T00:00:00Z --format json
```

## Exports

Export the raw snapshot or a report:

```bash
organizational-memory export json --store memory.json --output snapshot.json
organizational-memory export csv --store memory.json
organizational-memory export markdown --store memory.json --target report \
  --report-type organizational-memory --now 2026-03-01T00:00:00Z --output memo.md
```

## Demos

```bash
organizational-memory demo startup
organizational-memory demo all
```

See [docs/demos.md](demos.md) for details on each demo and the bundled datasets.

## Configuration

```bash
organizational-memory config show
organizational-memory config init --path organizational_memory.config.json
organizational-memory config set-store --store memory.json --backend json
organizational-memory config validate --path organizational_memory.config.json
```

## Troubleshooting

- **`error: cannot read transcript`** — check the file path and permissions.
- **`error: --meeting-id is required for the meeting report`** — pass
  `--meeting-id` when generating a meeting report.
- **`error: --start and --end are required for the weekly report`** — provide
  both window bounds as ISO-8601 timestamps.
- **`No results.` / empty listings** — the store may be empty; ingest a
  transcript first, or check the `--store`/`--backend` you passed.
- **Non-reproducible analytics/report output** — pass an explicit `--now` so
  time-dependent calculations are deterministic.
- **`benchmark script not found`** — the script-backed benchmarks require the
  repository checkout (the `scripts/` directory); the `analytics` benchmark works
  from the installed package alone.

## Limitations

- All behavior is rule-based and deterministic; there is no predictive modeling.
- The CLI is a local tool and provides examples and deterministic demos; it is
  not a hosted product or service.
