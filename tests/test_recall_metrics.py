"""Tests for recall metrics."""

import pytest

from organizational_memory.recall.metrics import (
    QueryOutcome,
    average_result_count,
    compute_metrics,
    hit_rate,
    mean_reciprocal_rank,
    top_k_hit_rate,
    zero_result_rate,
)


def _outcomes() -> list[QueryOutcome]:
    return [
        QueryOutcome(expected_ids=("a",), returned_ids=("a", "b", "c")),
        QueryOutcome(expected_ids=("x",), returned_ids=("y", "x")),
        QueryOutcome(expected_ids=("z",), returned_ids=()),
    ]


def test_hit_rate() -> None:
    assert hit_rate(_outcomes()) == pytest.approx(2 / 3)


def test_top_k_hit_rate() -> None:
    assert top_k_hit_rate(_outcomes(), k=1) == pytest.approx(1 / 3)
    assert top_k_hit_rate(_outcomes(), k=2) == pytest.approx(2 / 3)


def test_mean_reciprocal_rank() -> None:
    # ranks: 1, 2, none -> (1 + 0.5 + 0) / 3
    assert mean_reciprocal_rank(_outcomes()) == pytest.approx(1.5 / 3)


def test_zero_result_rate() -> None:
    assert zero_result_rate(_outcomes()) == pytest.approx(1 / 3)


def test_average_result_count() -> None:
    assert average_result_count(_outcomes()) == pytest.approx(5 / 3)


def test_compute_metrics_bundle() -> None:
    metrics = compute_metrics(_outcomes(), k=2)
    assert metrics.k == 2
    assert metrics.hit_rate == pytest.approx(2 / 3, abs=1e-6)
    assert metrics.zero_result_rate == pytest.approx(1 / 3, abs=1e-6)


def test_empty_outcomes() -> None:
    assert compute_metrics([]).hit_rate == 0.0
