"""Tests for the benchmark CLI command."""

import pytest

from organizational_memory.cli.main import main


def test_analytics_benchmark(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["benchmark", "analytics"]) == 0
    out = capsys.readouterr().out
    assert "Analytics benchmark" in out
    assert "health_grade:" in out


def test_extraction_benchmark(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["benchmark", "extraction"]) == 0
    assert capsys.readouterr().out.strip()


def test_all_benchmark(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["benchmark", "all"]) == 0
    out = capsys.readouterr().out
    assert "Analytics benchmark" in out


def test_unknown_benchmark_exits_nonzero() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["benchmark", "nope"])
    assert excinfo.value.code != 0


def test_analytics_benchmark_deterministic(
    capsys: pytest.CaptureFixture[str]
) -> None:
    main(["benchmark", "analytics"])
    first = capsys.readouterr().out
    main(["benchmark", "analytics"])
    second = capsys.readouterr().out
    assert first == second
