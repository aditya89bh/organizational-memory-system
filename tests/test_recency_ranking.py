"""Tests for recency ranking."""

from datetime import timedelta

import pytest

from organizational_memory.models import Decision
from organizational_memory.recall.ranking.recency import (
    recency_score,
    relevant_timestamp,
)
from organizational_memory.utils.time import utc_now


def test_recent_record_scores_one() -> None:
    now = utc_now()
    decision = Decision(title="x", description="y", created_at=now, updated_at=now)
    assert recency_score(decision, now=now) == 1.0


def test_older_record_scores_lower() -> None:
    now = utc_now()
    old = Decision(
        title="x",
        description="y",
        created_at=now - timedelta(days=60),
        updated_at=now - timedelta(days=60),
    )
    recent = Decision(title="a", description="b", created_at=now, updated_at=now)
    assert recency_score(old, now=now) < recency_score(recent, now=now)


def test_half_life_halves_score() -> None:
    now = utc_now()
    decision = Decision(
        title="x",
        description="y",
        created_at=now - timedelta(days=30),
        updated_at=now - timedelta(days=30),
    )
    assert recency_score(decision, now=now, half_life_days=30.0) == pytest.approx(
        0.5, abs=1e-6
    )


def test_relevant_timestamp_picks_latest() -> None:
    now = utc_now()
    decision = Decision(
        title="x",
        description="y",
        created_at=now - timedelta(days=10),
        updated_at=now - timedelta(days=1),
    )
    assert relevant_timestamp(decision) == decision.updated_at


def test_invalid_half_life_raises() -> None:
    with pytest.raises(ValueError, match="half_life_days"):
        recency_score(Decision(title="x", description="y"), half_life_days=0)
