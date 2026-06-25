# Recall evaluation

This document describes how recall quality is measured in the Organizational
Memory System. Evaluation is **deterministic and offline**: it runs fixed
queries against a fixed fixture dataset and compares the returned record ids
against the expected ids. There are no embeddings, LLMs, or network calls.

## Benchmark design

The benchmark harness lives in
[`scripts/run_recall_benchmarks.py`](../scripts/run_recall_benchmarks.py). It:

1. Builds a small, deterministic fixture store (a `JSONStore` in a temporary
   directory) containing decisions, tasks, open loops, and a commitment.
2. Runs a set of representative benchmark cases. Each case pairs a query with the
   record ids it is expected to return and a callable that executes the query
   (keyword search, record-specific search, the query parser, or
   natural-language recall).
3. Compares expected ids against returned ids and reports per-case hit rate plus
   overall hit rate and top-k accuracy.

Each case is a `BenchmarkCase(name, expected_ids, run)`. Running a case produces
a `CaseResult` exposing:

- `hit_rate` — fraction of expected ids present anywhere in the returned ids.
- `top_k_hit` — whether every expected id appears within the top `TOP_K` (3)
  results.

## Metrics

The reusable metric functions live in
[`src/organizational_memory/recall/metrics.py`](../src/organizational_memory/recall/metrics.py)
and operate over `QueryOutcome(expected_ids, returned_ids)` values:

- **hit rate** — mean fraction of expected ids found anywhere in the results.
- **top-k hit rate** — fraction of queries with at least one expected id in the
  top `k`.
- **mean reciprocal rank** — average of `1 / rank` of the first relevant result.
- **zero-result rate** — fraction of queries that returned nothing.
- **average result count** — mean number of results returned per query.

`compute_metrics(outcomes, k)` returns all of these as a `RecallMetrics` bundle.

## Fixture expectations

The fixture dataset and expected results are intentionally small so they can be
reasoned about by hand:

| Case | Query | Expected ids |
| --- | --- | --- |
| `keyword_kubernetes` | keyword `kubernetes` | `d1` |
| `decision_accepted` | decisions with status `accepted` | `d1` |
| `tasks_alice` | tasks owned by `alice` | `t1` |
| `unresolved_open_loops` | "What is still unresolved?" | `o1` |
| `overdue_items` | "What is overdue?" | `c1` |
| `parser_pricing` | `type:decision pricing` | `d2` |

## Sample benchmark output

```text
Recall benchmarks
=================
keyword_kubernetes     expected=['d1'] returned=['d1'] hit_rate=1.00
decision_accepted      expected=['d1'] returned=['d1'] hit_rate=1.00
tasks_alice            expected=['t1'] returned=['t1'] hit_rate=1.00
unresolved_open_loops  expected=['o1'] returned=['o1'] hit_rate=1.00
overdue_items          expected=['c1'] returned=['c1'] hit_rate=1.00
parser_pricing         expected=['d2'] returned=['d2'] hit_rate=1.00
Total queries: 6
Overall hit rate: 1.00
Top-3 accuracy: 1.00
```

Run it yourself with:

```bash
python scripts/run_recall_benchmarks.py
```

## Limitations

- The fixture set is small and curated; it validates correctness and
  determinism, not large-scale ranking quality.
- Matching is lexical. Synonyms, stemming beyond simple tokenization, and
  semantic similarity are out of scope by design.
- Natural-language recall covers a conservative set of question shapes; anything
  unrecognized falls back to plain keyword search.
- Time-sensitive cases (recency, overdue) depend on a supplied reference time so
  results stay reproducible.
