# Reporting walkthrough

Phase 7 turns persisted organizational memory into deterministic, local reports
and exports. Every report is reproducible from explicit inputs: given the same
store contents (and the same `now` / date range where applicable), report
generation always produces byte-for-byte identical output. No LLMs, embeddings,
external APIs, or network calls are involved.

## The report model

All reports are built from a small shared model in
`organizational_memory.reports.base`:

- `Report` — a titled, timestamped container with a `summary` mapping,
  an ordered list of `sections`, and a `metadata` mapping.
- `ReportSection` — a named section with an optional bullet `body`,
  a `metrics` mapping, and zero or more `tables`.
- `ReportTable` — a titled table with `columns` and string `rows`.

`Report.to_dict()` returns a deterministic, JSON-safe structure (datetimes are
formatted as UTC ISO-8601 strings and enums become their values).

## Generating reports

Each report is a function that takes a `MemoryStore` and returns a `Report`.
Time-sensitive reports accept an explicit `now` (and date range) so results stay
reproducible.

```python
from organizational_memory.reports.meeting_summary import meeting_summary
from organizational_memory.reports.decision_report import decision_report
from organizational_memory.reports.commitment_report import commitment_report
from organizational_memory.reports.open_loop_report import open_loop_report
from organizational_memory.reports.weekly_report import weekly_report
from organizational_memory.reports.monthly_report import monthly_report
from organizational_memory.reports.timeline_report import timeline_report
from organizational_memory.reports.participant_report import participant_report
from organizational_memory.reports.accountability_report import accountability_report
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.reports.follow_up_report import follow_up_report

meeting = meeting_summary(store, "m1", now=now)
decisions = decision_report(store, now=now)
commitments = commitment_report(store, now=now)
open_loops = open_loop_report(store, now=now)
weekly = weekly_report(store, start=start, end=end, now=end)
monthly = monthly_report(store, start=start, end=end, now=end)
timeline = timeline_report(store, now=now)
participant = participant_report(store, "alice", now=now)
accountability = accountability_report(store, now=now)
overview = organizational_memory_report(store, now=now)
follow_ups = follow_up_report(store, now=now)
```

### Weekly and monthly reports

`weekly_report` and `monthly_report` operate on a half-open window
`[start, end)`. Creation timing uses `created_at` (and `decided_at` for
decisions); completion and resolution timing uses `updated_at`, so callers can
drive those deterministically in tests and fixtures.

## Templates

`organizational_memory.reports.templates` provides reusable templates that curate
existing reports into focused views by selecting and relabeling sections. They
add no new computation:

- `executive_summary(store)`
- `meeting_summary_template(store, meeting_id)`
- `weekly_review(store, start=..., end=...)`
- `open_loop_review(store)`
- `follow_up_memo(store)`

## Exporting

Exporters live under `organizational_memory.reports.exporters` and implement a
common `ReportExporter` interface (`export(report)`, `supported_extension`,
`content_type`).

```python
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.reports.exporters.json import JSONExporter
from organizational_memory.reports.exporters.csv import CSVExporter

markdown = MarkdownExporter().export(weekly)   # headings, bullets, tables
document = JSONExporter().export(weekly)        # stable key ordering, JSON-safe
tables = CSVExporter().export(weekly)           # one CSV block per report table
```

- **Markdown** renders headings, a metadata block, summary/metrics bullets,
  body bullets, and GitHub-style tables (pipes in cells are escaped).
- **JSON** serializes `Report.to_dict()` with sorted keys; datetimes and enums
  are normalized before serialization.
- **CSV** emits each report table as a block (title row, header row, data rows)
  with standard quoting; empty tables still emit their header.

## How reports use analytics

Several reports are thin, deterministic presentations of Phase 6 analytics:

- `weekly_report` and `monthly_report` use overdue, ownership, bottleneck,
  accountability, decision-velocity, commitment-completion, repeated-discussion,
  and memory-health analytics.
- `accountability_report` wraps the accountability metrics.
- `organizational_memory_report` combines memory health, bottlenecks, dependency
  analytics, repeated discussions, and open-loop metrics into one overview.
- `follow_up_report` combines open work, dependency blockers, and the oldest
  unresolved open loops.

## Example workflow: transcript to report

1. Extract structured records from a transcript with the Phase 3 extraction
   pipeline.
2. Persist them with a Phase 4 store (`JSONStore` or `SQLiteStore`).
3. Generate a report (e.g. `meeting_summary` or `weekly_report`).
4. Export it with the Markdown, JSON, or CSV exporter.

Runnable, deterministic examples live under `examples/reports/`, and sample
rendered outputs live under [assets/](assets/):

- [sample_meeting_summary.md](assets/sample_meeting_summary.md)
- [sample_weekly_report.md](assets/sample_weekly_report.md)
- [sample_follow_up_report.md](assets/sample_follow_up_report.md)
- [sample_memory_report.md](assets/sample_memory_report.md)

## Limitations

- Reports describe and summarize stored memory deterministically; they do not
  predict outcomes or make employee-performance judgements.
- A true memory-health *trend* requires historical snapshots, which are not
  stored; the monthly report shows the current health snapshot instead.
- Report quality depends entirely on the quality of the extracted and persisted
  records.
