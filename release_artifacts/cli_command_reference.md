# CLI command reference — v0.1.0

The `organizational-memory` command is local and deterministic. Run any command
with `--help` for full options.

```
organizational-memory <command> [options]
```

| Command | Description |
| --- | --- |
| `ingest` | Extract a transcript or notes file and persist the memory. |
| `recall` | Search organizational memory with a deterministic query. |
| `report` | Generate a deterministic report from the store. |
| `analytics` | Show deterministic workflow analytics for the store. |
| `commitments` | List and filter commitments. |
| `open-loops` | List and filter open loops. |
| `export` | Export a memory snapshot or a report. |
| `config` | Show, initialize, validate, or update local configuration. |
| `demo` | Run a bundled, deterministic demo. |
| `benchmark` | Run deterministic benchmarks. |

## Examples

```bash
organizational-memory ingest meeting.txt --store memory.json --meeting-id sync-1
organizational-memory recall "type:decision launch" --store memory.json --explain
organizational-memory report follow-up --store memory.json --now 2026-03-01T00:00:00Z
organizational-memory analytics --store memory.json --now 2026-03-01T00:00:00Z
organizational-memory export json --store memory.json --output snapshot.json
organizational-memory demo startup
```

Time-relative output is reproducible because the reference time is supplied
explicitly via `--now`. See [docs/user_guide.md](../docs/user_guide.md) for every
option.
