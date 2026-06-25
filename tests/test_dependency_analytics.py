"""Tests for dependency analytics."""

from pathlib import Path

from organizational_memory.analytics.dependency_analytics import (
    dependency_analytics,
)
from organizational_memory.models import Dependency
from organizational_memory.models.enums import DependencyStatus
from organizational_memory.storage.json_store import JSONStore


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    # Chain: a depends on b, b depends on c
    store.save_record(Dependency(id="x1", source_id="a", target_id="b"))
    store.save_record(Dependency(id="x2", source_id="b", target_id="c"))
    # c is also blocked-upon by d
    store.save_record(Dependency(id="x3", source_id="d", target_id="c"))
    # resolved dependency should be ignored
    store.save_record(
        Dependency(
            id="x4",
            source_id="e",
            target_id="f",
            status=DependencyStatus.RESOLVED,
        )
    )
    return store


def test_totals(tmp_path: Path) -> None:
    report = dependency_analytics(_store(tmp_path))
    assert report.total == 4
    assert report.active_blockers == 3


def test_blocked_records(tmp_path: Path) -> None:
    report = dependency_analytics(_store(tmp_path))
    assert report.blocked_records == ("a", "b", "d")


def test_blocking_counts_and_multi(tmp_path: Path) -> None:
    report = dependency_analytics(_store(tmp_path))
    assert report.blocking_counts == {"b": 1, "c": 2}
    assert report.multi_blockers == {"c": 2}


def test_dependency_chain(tmp_path: Path) -> None:
    report = dependency_analytics(_store(tmp_path))
    assert ("a", "b", "c") in report.chains
    assert report.longest_chain == 3


def test_cycle_is_safe(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "cycle.json")
    store.save_record(Dependency(id="c1", source_id="a", target_id="b"))
    store.save_record(Dependency(id="c2", source_id="b", target_id="a"))
    report = dependency_analytics(store)
    assert report.active_blockers == 2
    # A pure cycle has no root, so no chains are emitted.
    assert report.chains == []


def test_empty(tmp_path: Path) -> None:
    report = dependency_analytics(JSONStore(tmp_path / "e.json"))
    assert report.total == 0
    assert report.chains == []
