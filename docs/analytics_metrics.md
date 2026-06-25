# Analytics metrics

The `organizational_memory.analytics` package computes **deterministic** workflow
metrics from persisted organizational memory. It uses no LLMs, embeddings,
external APIs, or network calls — every metric is a pure function of the records
in a `MemoryStore` and, where time matters, an explicit `now` reference.

All time-sensitive metrics accept a `now` argument so results are reproducible.
Weekly buckets use ISO week labels (`YYYY-Www`); daily buckets use ISO calendar
dates (`YYYY-MM-DD`). Ratios are rounded to six decimal places.

## Conventions

- **Open vs. terminal status.** A record is *open* when its status is not in the
  terminal set (`completed`, `done`, `resolved`, `closed`, `cancelled`,
  `dismissed`, `mitigated`, `rejected`, `superseded`, `accepted`).
- **Overdue.** A record is overdue when it has a `due_at` in the past (relative
  to `now`) and is still open.
- **Owner / meeting fallback.** Missing owners are bucketed as `unassigned`;
  missing source meetings as `none`.

---

## Decision velocity

- **Module:** `analytics/decision_velocity.py` — `decision_velocity(store)`
- **Inputs:** `Decision` records.
- **Outputs:** total, decisions per ISO week, by meeting, by owner, plus `active`
  (proposed/accepted) and `superseded` counts.
- **Formula:** week bucket = `iso_week(decided_at or created_at)`.
- **Limitations:** velocity reflects recorded decisions only; it does not weigh
  decision impact.

```text
total=3 active=2 superseded=1
per_week={"2026-W06": 2, "2026-W07": 1}
```

## Commitment completion

- **Module:** `analytics/commitment_completion.py` — `commitment_completion(store)`
- **Inputs:** `Commitment` records.
- **Outputs:** total, open, completed, cancelled, completion rate, completed by
  owner, completed by meeting.
- **Formula:** `completion_rate = completed / total`.
- **Limitations:** completion is based on status only; there is no notion of
  partial progress.

## Open loop metrics

- **Module:** `analytics/open_loop_metrics.py` — `open_loop_metrics(store, now=...)`
- **Inputs:** `OpenLoop` records.
- **Outputs:** total, unresolved, resolved, average age (days) of unresolved
  loops, oldest unresolved items, by owner, by meeting.
- **Formula:** `age_days = (now - created_at) / 1 day`; average over unresolved.
- **Limitations:** age uses creation time, not last-touch time.

## Overdue tasks

- **Module:** `analytics/overdue_tasks.py` — `overdue_tasks(store, now=...)`
- **Inputs:** `Task`, `Commitment`, `OpenLoop` records.
- **Outputs:** total overdue, counts per type, by owner, by meeting, and a sorted
  list of overdue items with `days_overdue`.
- **Formula:** overdue when `due_at < now` and status is open.
- **Limitations:** records without a due date are never overdue.

## Ownership metrics

- **Module:** `analytics/ownership_metrics.py` — `ownership_metrics(store, now=...)`
- **Inputs:** owner-bearing records (`Decision`, `Commitment`, `Task`,
  `OpenLoop`, `Risk`, `ActionItem`).
- **Outputs:** records by owner, open by owner, overdue by owner, decisions by
  owner, risks by owner, and the count of unowned records.
- **Limitations:** ownership is a single-owner model; shared ownership is not
  represented.

## Meeting effectiveness

- **Module:** `analytics/meeting_effectiveness.py` — `meeting_effectiveness(store)`
- **Inputs:** `Meeting` records plus their attributed structured outputs.
- **Outputs:** per-meeting counts of decisions, commitments, tasks, open loops,
  risks, total structured outputs, and an effectiveness score.
- **Formula:** `score = signal / (signal + open_loops)` where
  `signal = decisions + commitments + tasks + risks`.
- **Limitations:** the score is a structural signal-to-noise indicator, **not** a
  measure of real meeting quality or productivity.

## Repeated discussions

- **Module:** `analytics/repeated_discussions.py` — `repeated_discussions(store)`
- **Inputs:** `DiscussionTopic` and `OpenLoop` records.
- **Outputs:** recurring topic clusters, recurring open-loop clusters, and
  keywords shared across multiple topics.
- **Formula:** records are grouped by normalized text (lowercased, tokenized);
  clusters with two or more members are reported.
- **Limitations:** matching is exact-after-normalization, so paraphrases are not
  detected.

## Dependency analytics

- **Module:** `analytics/dependency_analytics.py` — `dependency_analytics(store)`
- **Inputs:** `Dependency` records (`source` depends on `target`).
- **Outputs:** total, active blockers, blocked records, blocking counts,
  multi-blockers, dependency chains, longest chain length.
- **Formula:** only non-resolved dependencies are active; chains are simple paths
  from root sources, computed cycle-safely.
- **Limitations:** chain discovery is bounded and pure cycles emit no chains.

## Bottlenecks

- **Module:** `analytics/bottlenecks.py` — `bottlenecks(store, now=...)`
- **Inputs:** combines overdue, repeated discussion, dependency, and meeting
  effectiveness signals.
- **Outputs:** overloaded owners, recurring unresolved clusters, blocked records,
  multi-blockers, and low-signal meetings (many open loops, few decisions).
- **Limitations:** thresholds are configurable but fixed per run; signals are
  heuristic.

## Accountability

- **Module:** `analytics/accountability.py` — `accountability(store, now=...)`
- **Inputs:** work records (`Task`, `Commitment`, `OpenLoop`, `ActionItem`).
- **Outputs:** assigned vs. unassigned counts, per-owner follow-through, unresolved
  load by owner, commitments without due dates, tasks without owners.
- **Formula:** `follow_through = completed / (completed + open)`.
- **Limitations:** follow-through is status-based and time-agnostic.

## Trends

- **Module:** `analytics/trends.py` — `trends(store, now=...)`
- **Inputs:** `Decision`, `Commitment`, `OpenLoop`, and overdue records.
- **Outputs:** weekly counts and change-from-previous-bucket for each series.
- **Limitations:** trends describe recorded activity, not forecasts.

## Timeline analytics

- **Module:** `analytics/timeline_analytics.py` — `timeline_analytics(store)`
- **Inputs:** all records.
- **Outputs:** activity by date, activity by type, busiest date, and the active
  date range.
- **Limitations:** each record contributes a single representative timestamp.

## Productivity

- **Module:** `analytics/productivity.py` — `productivity(store)`
- **Inputs:** work records, structured outputs, meetings.
- **Outputs:** closed-work ratio, structured outputs per meeting, completed
  commitments per week, unresolved-work ratio.
- **Limitations:** these are **structural** indicators and must not be read as
  individual performance measures.

## Memory health

- **Module:** `analytics/memory_health.py` — `memory_health(store, now=...)`
- **Inputs:** open loops, work records, decisions, repeated discussions, metadata.
- **Outputs:** a 0–100 score, letter grade, weighted components, and
  recommendations.
- **Formula:** weighted average of six 0–1 sub-scores (open-loop resolution,
  overdue work, ownership coverage, decision freshness, discussion focus,
  metadata completeness). Grade thresholds: A≥90, B≥80, C≥70, D≥60, else F.
- **Limitations:** weights are fixed; the score summarizes hygiene, not outcomes.

```text
score=65.0 grade=D
components: open_loop_resolution, overdue_work, ownership_coverage,
            decision_freshness, discussion_focus, metadata_completeness
```

## Report and dashboard

- **Module:** `analytics/reporting.py` — `generate_report(store, now=...)` and
  `build_dashboard_snapshot(store, now=...)`.
- **Outputs:** a structured `AnalyticsReport` (summary, key metrics, risks,
  bottlenecks, owner load, recommendations) and a JSON-safe `DashboardSnapshot`.

## Benchmark fixtures

Deterministic fixtures live under [`examples/analytics/`](../examples/analytics):
`analytics_memory_snapshot.json` (a loadable store), `analytics_meetings.json`,
and `analytics_expected_metrics.json` (expected values at a fixed `now`). The
test suite loads these to guard against regressions.
