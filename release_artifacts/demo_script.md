# Demo script — v0.1.0

A short, copy-pasteable script for demonstrating the toolkit end to end. Every
step is local and deterministic.

## 1. Install

```bash
pip install -e .
```

## 2. Run a self-contained demo

```bash
organizational-memory demo --list
organizational-memory demo startup
organizational-memory demo all
```

Each demo ingests a fixed transcript, extracts structured memory, and prints
deterministic recall/analytics/report output — entirely in memory.

## 3. Build your own memory store

```bash
# Ingest a sample transcript into a local JSON store
organizational-memory ingest examples/transcripts/startup_product_meeting.txt \
  --store memory.json --backend json

# Recall across the stored memory
organizational-memory recall "launch" --store memory.json
organizational-memory recall "type:decision" --store memory.json --explain

# Generate reports and analytics at a fixed reference time
organizational-memory analytics --store memory.json --now 2026-03-01T00:00:00Z
organizational-memory report weekly --store memory.json --now 2026-03-01T00:00:00Z
```

## 4. Walk through the tutorials

```bash
python examples/tutorials/tutorial_01_ingest_and_extract.py
python examples/tutorials/tutorial_02_persist_and_recall.py
python examples/tutorials/tutorial_03_analytics_and_reports.py
python examples/tutorials/tutorial_04_full_workflow.py
```

For more, see [docs/case_studies.md](../docs/case_studies.md) and
[docs/examples_gallery.md](../docs/examples_gallery.md).
