"""Inspectable traces describing how a recall query was executed.

A :class:`RecallTrace` records each stage of a query: the query received, the
filters applied, the candidate set considered, the ranking strategy used, and
the results returned. Traces are built incrementally and are purely descriptive.
"""

from dataclasses import dataclass, field

from organizational_memory.recall.engine import RecallResult


@dataclass(frozen=True)
class TraceStage:
    """A single, ordered step in a recall trace."""

    name: str
    detail: str


@dataclass(frozen=True)
class RecallTrace:
    """A structured, ordered description of a recall execution."""

    query: str
    filters: dict[str, str] = field(default_factory=dict)
    candidate_count: int = 0
    ranking: str = "none"
    result_ids: tuple[str, ...] = ()
    stages: tuple[TraceStage, ...] = ()


class RecallTraceBuilder:
    """Accumulates trace stages and produces a :class:`RecallTrace`."""

    def __init__(self, query: str) -> None:
        self._query = query
        self._filters: dict[str, str] = {}
        self._candidate_count = 0
        self._ranking = "none"
        self._result_ids: tuple[str, ...] = ()
        self._stages: list[TraceStage] = [
            TraceStage(name="query_received", detail=query)
        ]

    def record_filters(self, **filters: object) -> "RecallTraceBuilder":
        """Record the active (non-None) filters applied to the query."""
        applied = {
            key: str(value) for key, value in filters.items() if value is not None
        }
        self._filters = applied
        detail = ", ".join(f"{key}={value}" for key, value in sorted(applied.items()))
        self._stages.append(
            TraceStage(name="filters_applied", detail=detail or "none")
        )
        return self

    def record_candidates(self, count: int) -> "RecallTraceBuilder":
        """Record how many candidate records were considered."""
        self._candidate_count = count
        self._stages.append(
            TraceStage(name="candidates_considered", detail=str(count))
        )
        return self

    def record_ranking(self, ranking: str) -> "RecallTraceBuilder":
        """Record the ranking strategy that was applied."""
        self._ranking = ranking
        self._stages.append(TraceStage(name="ranking_applied", detail=ranking))
        return self

    def record_results(self, results: list[RecallResult]) -> "RecallTraceBuilder":
        """Record the ids of the results returned."""
        self._result_ids = tuple(result.record.id for result in results)
        self._stages.append(
            TraceStage(name="results_returned", detail=str(len(results)))
        )
        return self

    def build(self) -> RecallTrace:
        """Return the assembled, immutable :class:`RecallTrace`."""
        return RecallTrace(
            query=self._query,
            filters=dict(self._filters),
            candidate_count=self._candidate_count,
            ranking=self._ranking,
            result_ids=self._result_ids,
            stages=tuple(self._stages),
        )
