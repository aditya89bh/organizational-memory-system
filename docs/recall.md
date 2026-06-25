# Recall & query engine

The `organizational_memory.recall` package retrieves records persisted by the
[storage layer](persistence.md) using **deterministic search and ranking only**.
There are no embeddings, LLMs, external APIs, or network calls. Every result is
explainable and reproducible.

## Architecture

Recall is built from small, composable pieces:

- **Search** modules find candidate records (keyword and per-record-type).
- **Ranking** modules score candidates (recency, importance, ownership, and a
  configurable composite).
- **Explanations** turn a result's structured details into human-readable
  reasons.
- **Traces** describe how a query was executed, stage by stage.
- **Pagination** windows results with navigation metadata.
- **Query parsing** turns compact and natural-language-like queries into
  structured filters.
- **Metrics** and **benchmarks** measure recall quality deterministically.

The shared result type is `RecallResult(record, score, matched_fields, details)`,
returned by every search.

## Search types

### Keyword search

`search_keywords(records, query)` performs lexical search across a record's text
fields. Queries and text are tokenized (lowercased, alphanumeric), matched
case-insensitively, and scored by token coverage with a bonus for exact phrase
matches. `score_record` exposes the per-record `KeywordMatch`.

### Record-specific search

Each function loads its record type from a `MemoryStore`, applies exact-match and
date-window filters, then ranks by keyword text when provided:

- `search_decisions` — title, description, rationale, owner, status, meeting.
- `search_commitments` — description, owner, status, due window, meeting.
- `search_tasks` — title, description, owner, priority, status, due window,
  meeting.
- `search_participants` — name, email, role, organization.
- `search_open_loops` — question, owner, status, due window, meeting.

### Timeline search

`search_timeline` collects time-bearing records (meetings, decisions,
commitments, tasks, open loops, risks, memory events), picks the most meaningful
timestamp for each, filters by an `after`/`before` window, and returns them in
ascending or descending order.

### Relationship search

`search_relationships` filters an iterable of `EntityRelationship` records by
source, target, relationship type, or a related entity id. Relationships are not
persisted in the stores, so they are passed in explicitly.

## Query parser

`parse_query` reads compact queries that mix free text with `key:value` filters
and returns a typed `ParsedQuery`:

```text
owner:aditya status:open kubernetes
type:decision after:2026-01-01 before:2026-02-01 pricing
priority:high severity:critical
```

Recognized keys are `type`, `owner`, `status`, `priority`, `severity`, `after`,
`before`, and `meeting`. Unknown `key:value` tokens are treated as free text, and
only malformed dates raise an error.

## Natural-language-like search

`answer(store, question)` maps a conservative set of question shapes onto
structured recall using rule-based heuristics — never an LLM. `interpret`
exposes the structured `Interpretation`. Supported shapes include:

- "Who owns the launch task?" → task search for "launch"
- "What decisions were made about pricing?" → decision search for "pricing"
- "What is still unresolved?" → open open-loops
- "What is overdue?" → past-due, non-terminal tasks/commitments/open loops
- "Why did we choose X?" → decision search for "X"

Unrecognized questions fall back to plain keyword search.

## Ranking

All ranking signals return scores in a bounded range and are deterministic:

- **Recency** (`recency_score`) — exponential decay on a record's most recent
  relevant timestamp; newer ranks higher.
- **Importance** (`importance_score`) — combines record-type weight, a
  severity/priority level, and a status weight (active items rank above terminal
  ones). An explicit `metadata["importance"]` overrides the computed value.
- **Ownership** (`ownership_score`) — relevance to a target owner via owner,
  actor, participant, or assignee.
- **Composite** (`composite_score`, `rank_composite`) — a weighted sum of the
  keyword, recency, importance, and ownership signals. Weights are configurable
  via `RankingWeights`, and the component breakdown is retained on each result.

## Explanations

`explain_result` / `explain_results` derive an `Explanation` from a result,
capturing the matched fields, matched tokens, phrase match, ranking components,
the final score, and a list of human-readable reasons.

## Traces

`RecallTraceBuilder` records each stage of a query — query received, filters
applied, candidates considered, ranking applied, and results returned — and
produces an immutable `RecallTrace` for inspection.

## Pagination

`paginate(items, limit=..., offset=...)` returns a `Page` with the windowed
items plus `total`, `offset`, `limit`, `returned`, and `has_more`. Use
`Page.as_metadata()` for JSON-compatible page metadata.

## Metrics

`organizational_memory.recall.metrics` evaluates recall quality over
`QueryOutcome` values: hit rate, top-k hit rate, mean reciprocal rank,
zero-result rate, and average result count. `compute_metrics` returns the full
`RecallMetrics` bundle. See [recall_evaluation.md](recall_evaluation.md) for the
benchmark harness and sample output.

## Examples

Runnable, deterministic examples live in [`examples/recall/`](../examples/recall):

- `keyword_search_example.py`
- `decision_recall_example.py`
- `open_loop_recall_example.py`
- `natural_language_recall_example.py`

```bash
python examples/recall/keyword_search_example.py
```

## Limitations

- Matching is lexical; there is no semantic similarity, stemming, or synonym
  expansion by design.
- Natural-language recall is intentionally conservative and rule-based.
- Time-sensitive ranking and queries take an explicit reference time so results
  stay reproducible.
- Relationship search operates on supplied relationships rather than the store,
  since relationships are not persisted.
