"""Tests for recall traces."""

from organizational_memory.models import Decision
from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.traces import RecallTraceBuilder


def test_trace_records_all_stages() -> None:
    results = [RecallResult(record=Decision(id="d1", title="x", description="y"))]
    trace = (
        RecallTraceBuilder("kubernetes owner:alice")
        .record_filters(owner="alice", status=None)
        .record_candidates(5)
        .record_ranking("composite")
        .record_results(results)
        .build()
    )

    assert trace.query == "kubernetes owner:alice"
    assert trace.filters == {"owner": "alice"}
    assert trace.candidate_count == 5
    assert trace.ranking == "composite"
    assert trace.result_ids == ("d1",)

    stage_names = [stage.name for stage in trace.stages]
    assert stage_names == [
        "query_received",
        "filters_applied",
        "candidates_considered",
        "ranking_applied",
        "results_returned",
    ]


def test_trace_excludes_none_filters() -> None:
    trace = RecallTraceBuilder("q").record_filters(owner=None, status=None).build()
    assert trace.filters == {}
    assert trace.stages[1].detail == "none"


def test_trace_minimal() -> None:
    trace = RecallTraceBuilder("just a query").build()
    assert trace.candidate_count == 0
    assert trace.ranking == "none"
    assert trace.result_ids == ()
    assert trace.stages[0].name == "query_received"
