# Examples gallery

A guided tour of everything runnable in the repository: sample transcripts,
storage and recall examples, analytics and report examples, demos, and tutorials.
Every command is local and deterministic.

Install first:

```bash
pip install -e .
```

## Transcripts

Sample inputs under [`examples/transcripts/`](../examples/transcripts/):

- `startup_product_meeting.txt`
- `sprint_planning_meeting.md`
- `board_review_meeting.txt`

Ingest one into a store:

```bash
organizational-memory ingest examples/transcripts/startup_product_meeting.txt \
  --store memory.json --backend json
```

## Storage examples

- [`examples/storage_demo.py`](../examples/storage_demo.py) — save and load
  records through the store interface.

```bash
python examples/storage_demo.py
```

## Recall examples

Under [`examples/recall/`](../examples/recall/):

- `keyword_search_example.py`
- `decision_recall_example.py`
- `open_loop_recall_example.py`
- `natural_language_recall_example.py`

```bash
python examples/recall/keyword_search_example.py
```

## Analytics examples

Under [`examples/analytics/`](../examples/analytics/):

- `analytics_report_example.py`
- `decision_velocity_example.py`
- `memory_health_example.py`
- `open_loop_metrics_example.py`

```bash
python examples/analytics/analytics_report_example.py
```

## Report examples

Under [`examples/reports/`](../examples/reports/):

- `meeting_summary_example.py`
- `weekly_report_example.py`
- `follow_up_report_example.py`
- `organizational_memory_report_example.py`

```bash
python examples/reports/weekly_report_example.py
```

## Demo examples

Reproducible end-to-end demos under [`examples/demos/`](../examples/demos/), also
available via the CLI:

```bash
organizational-memory demo --list
organizational-memory demo startup
python examples/demos/startup_meeting_demo.py
```

See [demos.md](demos.md) for details.

## Tutorial scripts

Step-by-step tutorials under [`examples/tutorials/`](../examples/tutorials/):

```bash
python examples/tutorials/tutorial_01_ingest_and_extract.py
python examples/tutorials/tutorial_02_persist_and_recall.py
python examples/tutorials/tutorial_03_analytics_and_reports.py
python examples/tutorials/tutorial_04_full_workflow.py
```

## Example datasets

Pre-built operating-memory snapshots under
[`examples/datasets/`](../examples/datasets/):

- `startup_operating_memory.json`
- `sprint_operating_memory.json`
- `board_operating_memory.json`
- `company_memory_full.json`

These can be loaded as JSON stores for recall, analytics, and reporting.
