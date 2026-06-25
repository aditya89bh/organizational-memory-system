"""Tests for the config CLI command."""

import json
from pathlib import Path

import pytest

from organizational_memory.cli.main import main


def test_show(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["config", "show"]) == 0
    out = capsys.readouterr().out
    assert "Application defaults" in out
    assert "CLI defaults" in out


def test_init_and_validate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "cfg.json"
    assert main(["config", "init", "--path", str(path)]) == 0
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["backend"] == "json"
    capsys.readouterr()
    assert main(["config", "validate", "--path", str(path)]) == 0
    assert "valid:" in capsys.readouterr().out


def test_init_existing_without_force(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "cfg.json"
    main(["config", "init", "--path", str(path)])
    capsys.readouterr()
    assert main(["config", "init", "--path", str(path)]) == 1
    assert "already exists" in capsys.readouterr().out


def test_validate_invalid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"backend": "redis"}', encoding="utf-8")
    assert main(["config", "validate", "--path", str(path)]) == 1
    assert "invalid:" in capsys.readouterr().out


def test_set_store(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "cfg.json"
    assert main(
        ["config", "set-store", "--path", str(path), "--store", "db.sqlite",
         "--backend", "sqlite"]
    ) == 0
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["store"] == "db.sqlite"
    assert data["backend"] == "sqlite"


def test_set_store_requires_value(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "cfg.json"
    assert main(["config", "set-store", "--path", str(path)]) == 1
