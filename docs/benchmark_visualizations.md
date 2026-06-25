# Benchmark visualizations

These are **text-only**, deterministic visualizations of the toolkit's behavior.
They focus on counts that are stable for a fixed input (records extracted, recall
hits, report sections, storage operations) rather than wall-clock timing, which
varies by machine. There are no images or binary assets.

To reproduce the underlying numbers:

```bash
python scripts/run_performance_benchmarks.py
python scripts/run_memory_benchmarks.py 200
python scripts/verify_package.py
```

The performance script reports elapsed time and operations per second (machine
dependent and intentionally not asserted); the counts shown below are
deterministic.

## Extraction

Records extracted per demo transcript (deterministic):

```
startup:  decisions 1  commitments 1  tasks 1  open_loops 1  risks 1  action_items 2
sprint:   decisions 1  commitments 2  tasks 1  open_loops 1  risks 0  action_items 3
board:    decisions 2  commitments 0  tasks 0  open_loops 1  risks 2  action_items 0
```

Full chart: [`extraction_summary.txt`](assets/benchmarks/extraction_summary.txt).

## Recall

Lexical recall over the combined demo memory (41 records):

```
query "launch"   -> 3 hits
query "pricing"  -> 2 hits
```

Full chart: [`recall_summary.txt`](assets/benchmarks/recall_summary.txt).

## Analytics

Analytics report over the combined demo memory yields a stable set of metric
groups and derived analytics (memory health, bottlenecks, owner load, decision
velocity, commitment completion, open-loop metrics, overdue tasks, productivity).

Full summary: [`analytics_summary.txt`](assets/benchmarks/analytics_summary.txt).

## Reports

The organizational-memory report renders 7 deterministic sections and exports
identically to Markdown, JSON, and CSV. A synthetic 200-record storage benchmark
estimates ~57 KB of JSON payload with matching JSON and SQLite operation counts.

Full summary: [`report_summary.txt`](assets/benchmarks/report_summary.txt).

## Package verification

All package-verification checks pass deterministically.

Full summary:
[`package_verification_summary.txt`](assets/benchmarks/package_verification_summary.txt).
