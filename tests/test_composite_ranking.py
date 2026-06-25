"""Tests for composite ranking."""

from datetime import timedelta

from organizational_memory.models import Task
from organizational_memory.models.enums import Priority, TaskStatus
from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.ranking.composite import (
    RankingWeights,
    composite_score,
    rank_composite,
)
from organizational_memory.utils.time import utc_now


def test_composite_components_present() -> None:
    now = utc_now()
    task = Task(title="x", description="y", owner_id="alice", created_at=now)
    scored = composite_score(task, keyword_score=1.0, now=now, owner="alice")
    assert set(scored.components) == {"keyword", "recency", "importance", "ownership"}
    assert scored.components["keyword"] == 1.0
    assert scored.components["ownership"] == 1.0
    assert scored.total > 0


def test_weights_affect_total() -> None:
    now = utc_now()
    task = Task(title="x", description="y", owner_id="alice", created_at=now)
    only_keyword = RankingWeights(
        keyword=1.0, recency=0.0, importance=0.0, ownership=0.0
    )
    scored = composite_score(
        task, keyword_score=0.5, now=now, owner="alice", weights=only_keyword
    )
    assert scored.total == 0.5


def test_rank_composite_orders_by_total() -> None:
    now = utc_now()
    owned = Task(
        id="t1",
        title="owned",
        description="y",
        owner_id="alice",
        priority=Priority.URGENT,
        status=TaskStatus.IN_PROGRESS,
        created_at=now,
    )
    other = Task(
        id="t2",
        title="other",
        description="y",
        owner_id="bob",
        priority=Priority.LOW,
        status=TaskStatus.DONE,
        created_at=now - timedelta(days=120),
    )
    results = [
        RecallResult(record=other, score=1.0),
        RecallResult(record=owned, score=1.0),
    ]
    ranked = rank_composite(results, now=now, owner="alice")
    assert [r.record.id for r in ranked] == ["t1", "t2"]
    assert "ranking" in ranked[0].details


def test_rank_composite_stable_tie_break() -> None:
    now = utc_now()
    a = Task(id="a", title="x", description="y", owner_id="z", created_at=now)
    b = Task(id="b", title="x", description="y", owner_id="z", created_at=now)
    results = [RecallResult(record=b, score=1.0), RecallResult(record=a, score=1.0)]
    ranked = rank_composite(results, now=now)
    assert [r.record.id for r in ranked] == ["a", "b"]
