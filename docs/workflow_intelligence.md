# Workflow intelligence

Phase 6 adds **deterministic workflow intelligence** on top of the persisted
organizational memory. Given the decisions, commitments, tasks, open loops,
risks, dependencies, meetings, and discussion topics already stored, the
`organizational_memory.analytics` package answers operational questions such as:
how fast are we deciding, what is overdue, who is overloaded, what keeps coming
back, and how healthy is our memory overall.

Everything here is computed locally and deterministically. There are no LLMs,
embeddings, external APIs, or network calls, and there is no predictive
modelling — the analytics describe what the records say, not what will happen.

## Architecture

The package is organized as a set of small, single-responsibility modules:

- **Per-metric modules** — `decision_velocity`, `commitment_completion`,
  `open_loop_metrics`, `overdue_tasks`, `ownership_metrics`,
  `meeting_effectiveness`, `repeated_discussions`, `dependency_analytics`,
  `accountability`, `trends`, `timeline_analytics`, `productivity`.
- **Composite modules** — `bottlenecks` and `memory_health` combine several
  signals into higher-level insights.
- **Presentation** — `dashboard` (typed JSON-safe models), `reporting`
  (`generate_report`, `build_dashboard_snapshot`), and `visualizations`
  (text-only ASCII charts).
- **Shared helpers** — `common` provides grouping, ISO bucketing, status
  vocabularies, and overdue logic reused across modules.

Each metric is a pure function of a `MemoryStore` (plus an explicit `now` where
time matters) and returns a frozen dataclass, which keeps results inspectable and
easy to test.

## How analytics use memory records

Analytics never re-parse transcripts; they read the already-structured records:

- **Decisions** drive velocity, freshness, and meeting effectiveness.
- **Commitments / tasks / open loops / action items** form the *work* whose
  completion, overdue status, ownership, and accountability are measured.
- **Risks** feed ownership and report risk listings.
- **Dependencies** (`source` depends on `target`) drive blocker and chain
  analysis.
- **Meetings** anchor per-meeting effectiveness and low-signal detection.
- **Discussion topics + open loops** power repeated-discussion detection.

Status interpretation is centralized: a record is *open* unless its status is in
a fixed terminal set, and *overdue* when its `due_at` is in the past while still
open.

## Bottlenecks

`bottlenecks(store, now=...)` combines four deterministic signals:

- **Overloaded owners** — owners whose overdue count meets a threshold.
- **Recurring unresolved topics** — repeated open-loop clusters.
- **Blocked records** — sources with active (non-resolved) dependencies, plus
  records that block many others.
- **Low-signal meetings** — meetings producing many open loops but few or no
  decisions.

These are heuristics meant to focus attention, not to assign blame.

## Accountability metrics

`accountability(store, now=...)` reports assigned vs. unassigned work, and for
each owner a follow-through score of `completed / (completed + open)`. It also
surfaces unresolved load per owner, commitments missing due dates, and tasks
missing owners. Scores are status-based and time-agnostic, so they describe
hygiene rather than individual performance.

## Repeated discussion detection

`repeated_discussions(store)` normalizes topic titles and open-loop questions
(lowercase + tokenize) and groups records by their normalized text. Clusters with
two or more members are reported with the records and meetings involved, alongside
keywords shared across multiple topics. Matching is exact-after-normalization, so
it catches verbatim recurrence and trivial variations but not paraphrases.

## Memory health

`memory_health(store, now=...)` produces a single 0–100 score and letter grade
from six weighted sub-scores: open-loop resolution, overdue work, ownership
coverage, decision freshness, discussion focus, and metadata completeness. Each
component is reported with its weight and a human-readable detail string, and
recommendations are emitted for any component below the healthy threshold. The
weights are fixed, so the score is a transparent, reproducible hygiene summary.

## Examples

Runnable, deterministic examples live under
[`examples/analytics/`](../examples/analytics):

```bash
python examples/analytics/decision_velocity_example.py
python examples/analytics/open_loop_metrics_example.py
python examples/analytics/memory_health_example.py
python examples/analytics/analytics_report_example.py
```

The same directory holds the benchmark fixtures
(`analytics_memory_snapshot.json`, `analytics_meetings.json`,
`analytics_expected_metrics.json`) used by the regression tests.

## Limitations

- Analytics reflect only what has been extracted and persisted; gaps in the
  memory become gaps in the metrics.
- Scores and "effectiveness" indicators are structural signals, not measures of
  real productivity, decision quality, or employee performance.
- Text matching is deterministic and literal; semantic similarity is out of
  scope.
- There is no forecasting — trends summarize past buckets only.

See [docs/analytics_metrics.md](analytics_metrics.md) for the per-metric
reference (formulas, inputs, limitations, and example output).
