"""Broad CLI coverage: help, version, and every subcommand."""

import argparse
from pathlib import Path

import pytest

from organizational_memory.cli.commands import register_all
from organizational_memory.cli.main import build_parser, main

_SUBCOMMANDS = [
    "ingest",
    "recall",
    "report",
    "analytics",
    "commitments",
    "open-loops",
    "export",
    "config",
    "demo",
    "benchmark",
]

TRANSCRIPT = """# Product Sync

Attendees: Aditya, Priya, Rahul

[10:00] Aditya: We decided to launch the beta on Friday.
[10:02] Priya: I will prepare the onboarding docs.
[10:04] Rahul: The launch is blocked by the security review.
[10:05] Aditya: What is our rollback plan?
Risk: the vendor might miss the deadline.
TODO: finalize the pricing page.
Topic: Beta launch
"""

NOW = "2026-03-01T00:00:00Z"


def test_help() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0


def test_version() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0


def test_no_args_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "usage:" in capsys.readouterr().out


@pytest.mark.parametrize("command", _SUBCOMMANDS)
def test_subcommand_help(
    command: str, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main([command, "--help"])
    assert excinfo.value.code == 0
    assert "usage:" in capsys.readouterr().out


def test_all_subcommands_registered() -> None:
    parser = build_parser()
    subactions = [
        action for action in parser._actions if hasattr(action, "choices")
        and action.dest == "command"
    ]
    assert subactions
    registered = set(subactions[0].choices or {})
    assert set(_SUBCOMMANDS) <= registered


def test_register_all_registers_subcommands() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    register_all(subparsers)
    registered = set(subparsers.choices)
    assert set(_SUBCOMMANDS) <= registered


def _seed(tmp_path: Path) -> Path:
    transcript = tmp_path / "meeting.txt"
    transcript.write_text(TRANSCRIPT, encoding="utf-8")
    store = tmp_path / "memory.json"
    assert main(
        ["ingest", str(transcript), "--store", str(store), "--meeting-id", "m1"]
    ) == 0
    return store


def test_full_command_surface(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = _seed(tmp_path)
    s = ["--store", str(store)]
    assert main(["recall", "launch", *s]) == 0
    assert main(["report", "follow-up", *s, "--now", NOW]) == 0
    assert main(["analytics", *s, "--now", NOW]) == 0
    assert main(["commitments", *s, "--now", NOW]) == 0
    assert main(["open-loops", *s, "--now", NOW]) == 0
    assert main(["export", "json", *s]) == 0
    assert main(["config", "show"]) == 0
    assert main(["demo", "startup"]) == 0
    assert main(["benchmark", "analytics"]) == 0
    assert capsys.readouterr().out.strip()
