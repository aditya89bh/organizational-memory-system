# Interactive walkthrough

This walkthrough shows a complete local workflow with the `organizational-memory`
command-line interface. Everything runs locally and deterministically: there are
no LLMs, embeddings, external APIs, or network calls.

## 1. Install the package

From the repository root, install into a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the `organizational-memory` console script. Verify it:

```bash
organizational-memory --version
organizational-memory --help
```

## 2. Ingest a transcript

Create a transcript file, for example `meeting.txt`:

```text
# Product Sync

Attendees: Aditya, Priya, Rahul

[10:00] Aditya: We decided to launch the beta on Friday.
[10:02] Priya: I will prepare the onboarding docs.
[10:04] Rahul: The launch is blocked by the security review.
[10:05] Aditya: What is our rollback plan?
Risk: the vendor might miss the deadline.
TODO: finalize the pricing page.
Topic: Beta launch
```

Ingest it into a JSON store and attach a meeting record:

```bash
organizational-memory ingest meeting.txt --store memory.json --meeting-id sync-1
```

The command prints an extraction summary (counts per record type).

## 3. Inspect extracted memory

List commitments and open loops that were extracted:

```bash
organizational-memory commitments --store memory.json
organizational-memory open-loops --store memory.json --unresolved
```

## 4. Run recall

Search the store with keywords or compact `key:value` filters:

```bash
organizational-memory recall "launch" --store memory.json
organizational-memory recall "type:decision launch" --store memory.json --explain
```

`--explain` shows why each result matched and how it was scored.

## 5. Run analytics

Compute deterministic workflow analytics. Pass `--now` for reproducible output:

```bash
organizational-memory analytics --store memory.json --now 2026-03-01T00:00:00Z
organizational-memory analytics --store memory.json --format json --now 2026-03-01T00:00:00Z
```

## 6. Generate a report

Generate any supported report as Markdown or JSON:

```bash
organizational-memory report follow-up --store memory.json --now 2026-03-01T00:00:00Z
organizational-memory report meeting --store memory.json --meeting-id sync-1 \
  --now 2026-03-01T00:00:00Z
```

## 7. Export output

Export the raw memory snapshot or a report in `json`, `markdown`, or `csv`:

```bash
organizational-memory export json --store memory.json --output snapshot.json
organizational-memory export csv --store memory.json --target report \
  --report-type decisions --now 2026-03-01T00:00:00Z --output decisions.csv
```

## 8. Run demos

Run the bundled, deterministic demos that show the full pipeline end to end:

```bash
organizational-memory demo startup
organizational-memory demo all
```

## Configuration

Show defaults, initialize a local config file, validate it, or set the store:

```bash
organizational-memory config show
organizational-memory config init --path organizational_memory.config.json
organizational-memory config set-store --store memory.json --backend json
organizational-memory config validate --path organizational_memory.config.json
```

## Notes and limitations

- All commands are deterministic given the same inputs and an explicit `--now`.
- The system extracts and organizes information using rule-based logic only.
- There is no predictive modeling and no external service dependency.
