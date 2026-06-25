"""End-to-end retrieval tests across the recall stack.

Exercises persistence, the query parser, keyword and record-specific search,
composite ranking, explanations, and pagination together against deterministic
fixtures.
"""

from datetime import timedelta
from pathlib import Path

import pytest

from organizational_memory.models import Commitment, Decision, OpenLoop, Task
from organizational_memory.models.enums import (
    DecisionStatus,
    OpenLoopStatus,
    Priority,
    TaskStatus,
)
from organizational_memory.recall.decision_search import search_decisions
from organizational_memory.recall.explanations import explain_results
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.recall.pagination import paginate
from organizational_memory.recall.query_parser import parse_query
from organizational_memory.recall.ranking.composite import rank_composite
from organizational_memory.recall.task_search import search_tasks
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


@pytest.fixture
def store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    memory = JSONStore(tmp_path / "memory.json")
    memory.save_record(
        Decision(
            id="d1",
            title="Adopt Kubernetes",
            description="run services on kubernetes",
            owner_id="alice",
            status=DecisionStatus.ACCEPTED,
            rationale="kubernetes scales well",
            created_at=now,
        )
    )
    memory.save_record(
        Decision(
            id="d2",
            title="Pricing model",
            description="kubernetes is unrelated here pricing",
            owner_id="bob",
            status=DecisionStatus.PROPOSED,
            created_at=now - timedelta(days=120),
        )
    )
    memory.save_record(
        Task(
            id="t1",
            title="Migrate cluster to kubernetes",
            description="ops work",
            owner_id="alice",
            priority=Priority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            created_at=now,
        )
    )
    memory.save_record(
        Task(
            id="t2",
            title="Write docs",
            description="documentation",
            owner_id="carol",
            status=TaskStatus.DONE,
            created_at=now - timedelta(days=200),
        )
    )
    memory.save_record(
        OpenLoop(id="o1", question="kubernetes networking?", status=OpenLoopStatus.OPEN)
    )
    memory.save_record(
        Commitment(
            id="c1",
            owner_id="alice",
            description="finalize kubernetes rollout",
            created_at=now - timedelta(days=2),
            due_at=now + timedelta(days=2),
        )
    )
    return memory


def test_persistence_roundtrip(store: JSONStore) -> None:
    assert len(store.list_records()) == 6
    assert store.get_record("Decision", "d1") is not None


def test_keyword_search_across_all_records(store: JSONStore) -> None:
    results = search_keywords(store.list_records(), "kubernetes")
    ids = {r.record.id for r in results}
    assert {"d1", "d2", "t1", "o1", "c1"} <= ids
    assert "t2" not in ids


def test_query_parser_drives_decision_search(store: JSONStore) -> None:
    parsed = parse_query("type:decision owner:alice kubernetes")
    assert parsed.record_type == "Decision"
    results = search_decisions(
        store, text=parsed.text, owner_id=parsed.owner
    )
    assert [r.record.id for r in results] == ["d1"]


def test_composite_ranking_prefers_recent_owned(store: JSONStore) -> None:
    now = utc_now()
    base = search_keywords(store.list_records(), "kubernetes")
    ranked = rank_composite(base, now=now, owner="alice")
    # d1 is recent and owned by alice; d2 is old and owned by bob.
    ranked_ids = [r.record.id for r in ranked]
    assert ranked_ids.index("d1") < ranked_ids.index("d2")
    assert "ranking" in ranked[0].details


def test_explanations_align_with_results(store: JSONStore) -> None:
    results = search_keywords(store.list_records(), "kubernetes rollout")
    explanations = explain_results(results)
    assert [e.record_id for e in explanations] == [r.record.id for r in results]
    assert any(e.matched_tokens for e in explanations)


def test_task_search_then_pagination(store: JSONStore) -> None:
    results = search_tasks(store)
    page = paginate(results, limit=1, offset=0)
    assert page.total == 2
    assert page.returned == 1
    assert page.has_more is True


def test_full_pipeline_parse_search_rank_paginate(store: JSONStore) -> None:
    now = utc_now()
    parsed = parse_query("kubernetes")
    results = search_keywords(store.list_records(), parsed.text)
    ranked = rank_composite(results, now=now, owner="alice")
    page = paginate(ranked, limit=2, offset=0)
    assert page.returned == 2
    assert page.total == len(results)
    assert page.items[0].record.id in {"d1", "t1", "c1"}
