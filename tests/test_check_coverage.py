"""Tests for the coverage gate helpers and CLI."""

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_coverage.py"


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("check_coverage", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cc = _load()


def test_parse_json() -> None:
    assert cc.parse_coverage_json({"totals": {"percent_covered": 91.5}}) == 91.5


def test_parse_json_invalid() -> None:
    with pytest.raises(ValueError, match="invalid coverage JSON"):
        cc.parse_coverage_json({"nope": 1})


def test_parse_text() -> None:
    text = "Name   Stmts   Miss  Cover\nTOTAL   100   10   90%\n"
    assert cc.parse_coverage_text(text) == 90.0


def test_parse_text_missing() -> None:
    with pytest.raises(ValueError, match="TOTAL"):
        cc.parse_coverage_text("no total here")


def test_evaluate() -> None:
    passed, message = cc.evaluate(90.0, 85.0)
    assert passed
    assert "PASS" in message
    failed, message = cc.evaluate(70.0, 85.0)
    assert not failed
    assert "FAIL" in message


def test_main_pass(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "coverage.json"
    path.write_text(json.dumps({"totals": {"percent_covered": 95.0}}), encoding="utf-8")
    code = cc.main(["--coverage-file", str(path), "--min", "80"])
    assert code == 0
    assert "PASS" in capsys.readouterr().out


def test_main_fail(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "coverage.json"
    path.write_text(json.dumps({"totals": {"percent_covered": 50.0}}), encoding="utf-8")
    code = cc.main(["--coverage-file", str(path), "--min", "80"])
    assert code == 1
    assert "FAIL" in capsys.readouterr().out


def test_main_missing_file(capsys: pytest.CaptureFixture[str]) -> None:
    code = cc.main(["--coverage-file", "does-not-exist.json"])
    assert code == 2
    assert "error:" in capsys.readouterr().out
