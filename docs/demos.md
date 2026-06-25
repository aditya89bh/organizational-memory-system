# Demos

The project ships with deterministic, runnable demos that exercise the full
pipeline — extraction, persistence, recall, analytics, and reporting — entirely
in memory. They use no LLMs, embeddings, external APIs, or network calls, and
their output never changes between runs.

Run any demo from the CLI:

```bash
organizational-memory demo startup
organizational-memory demo all
```

Or run the standalone example scripts:

```bash
python examples/demos/startup_meeting_demo.py
```

Or call them programmatically:

```python
from organizational_memory.demos import run_demo, run_all

lines = run_demo("startup")
combined = run_all()
```

## Available demos

### Startup demo (`startup`)

Source: [`examples/demos/startup_meeting_demo.py`](../examples/demos/startup_meeting_demo.py)

Ingests a startup standup transcript, extracts decisions, commitments, tasks,
and open loops, persists them, and prints a deterministic follow-up report. A
captured run is stored at
[`docs/assets/cli_captures/demo_output.txt`](assets/cli_captures/demo_output.txt).

### Sprint planning demo (`sprint`)

Source: [`examples/demos/sprint_planning_demo.py`](../examples/demos/sprint_planning_demo.py)

Ingests sprint planning notes, identifies tasks and commitments, detects
blockers (dependencies) and open loops, and prints a weekly report for the
seven-day window ending at the reference time.

### Board meeting demo (`board`)

Source: [`examples/demos/board_meeting_demo.py`](../examples/demos/board_meeting_demo.py)

Ingests a board review transcript, extracts decisions and risks, and prints a
decision report followed by an organizational memory report.

### Organizational timeline demo (`timeline`)

Source: [`examples/demos/organizational_timeline_demo.py`](../examples/demos/organizational_timeline_demo.py)

Ingests several meetings spread across time and prints timeline analytics
(first/last/busiest dates) and a timeline report of chronological activity.

### Company memory demo (`company-memory`)

Source: [`examples/demos/company_memory_demo.py`](../examples/demos/company_memory_demo.py)

Answers four deterministic questions against the persisted memory using recall
and reports:

- Why did we delay the launch?
- Who owns the website redesign?
- What is still unresolved?
- What is overdue?

## Benchmark demo

The benchmark command runs deterministic benchmarks and reports counts and
accuracy where applicable:

```bash
organizational-memory benchmark extraction
organizational-memory benchmark all
```

The `extraction`, `recall`, and `reports` benchmarks wrap the scripts under
[`scripts/`](../scripts/); the `analytics` benchmark builds a store from the
bundled demo transcripts and summarizes the generated analytics report.

## Example datasets

Pre-built, deterministic operating-memory snapshots live under
[`examples/datasets/`](../examples/datasets/) and can be loaded directly with a
`JSONStore`:

- `startup_operating_memory.json`
- `sprint_operating_memory.json`
- `board_operating_memory.json`
- `company_memory_full.json`

## Expected outputs

Captured terminal output for the core commands is stored under
[`docs/assets/cli_captures/`](assets/cli_captures/) and is regression-tested for
determinism.

## Limitations

- Demos illustrate behavior on small, curated transcripts; they are not
  benchmarks of real-world extraction accuracy.
- All logic is rule-based and deterministic; there is no predictive modeling.
- Reference times are fixed so output is reproducible across machines.
