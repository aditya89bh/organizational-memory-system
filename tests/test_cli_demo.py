"""Tests for the demo CLI command."""

import pytest

from organizational_memory.cli.main import main


@pytest.mark.parametrize(
    "name", ["startup", "sprint", "board", "timeline", "company-memory"]
)
def test_demo_command(name: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["demo", name]) == 0
    assert capsys.readouterr().out.strip()


def test_demo_all(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["demo", "all"]) == 0
    out = capsys.readouterr().out
    assert "Startup meeting demo" in out
    assert "Board meeting demo" in out


def test_demo_unknown_exits_nonzero() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["demo", "does-not-exist"])
    assert excinfo.value.code != 0
