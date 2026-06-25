"""Tests for the bundled deterministic demos."""

import pytest

from organizational_memory.demos import (
    available_demos,
    run_all,
    run_demo,
)


def test_available_demos() -> None:
    names = available_demos()
    assert names == ["startup", "sprint", "board", "timeline", "company-memory"]


@pytest.mark.parametrize("name", available_demos())
def test_demo_runs_and_is_deterministic(name: str) -> None:
    first = run_demo(name)
    second = run_demo(name)
    assert first == second
    assert first
    assert isinstance(first[0], str)


def test_run_all_combines() -> None:
    combined = run_all()
    assert "Startup meeting demo" in combined
    assert "Company memory demo" in combined


def test_unknown_demo() -> None:
    with pytest.raises(ValueError, match="unknown demo"):
        run_demo("nope")


def test_startup_extracts_decision() -> None:
    lines = run_demo("startup")
    assert any(line.startswith("decisions: ") for line in lines)


def test_company_memory_answers() -> None:
    lines = run_demo("company-memory")
    text = "\n".join(lines)
    assert "Why did we delay the launch?" in text
    assert "Who owns the website redesign?" in text
    assert "What is overdue?" in text
