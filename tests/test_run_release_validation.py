"""Tests for the release validation orchestrator helpers."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "run_release_validation.py"
)


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("run_release_validation", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


rv = _load()


def test_read_pyproject_version() -> None:
    assert rv.read_pyproject_version() == "0.1.0"


def test_version_consistency_pass() -> None:
    result = rv.check_version_consistency("0.1.0", "0.1.0")
    assert result.passed


def test_version_consistency_fail() -> None:
    result = rv.check_version_consistency("0.1.0", "0.2.0")
    assert not result.passed


def test_required_paths_pass() -> None:
    result = rv.check_required_paths(rv.REQUIRED_DOCS, "required_docs")
    assert result.passed


def test_required_paths_fail(tmp_path: Path) -> None:
    result = rv.check_required_paths(("missing.md",), "required_docs", root=tmp_path)
    assert not result.passed


def test_scan_forbidden_detects(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text(rv.FORBIDDEN_STRINGS[0].upper(), encoding="utf-8")
    offenders = rv.scan_forbidden([bad], root=tmp_path)
    assert offenders


def test_scan_forbidden_clean(tmp_path: Path) -> None:
    good = tmp_path / "good.md"
    good.write_text("a perfectly clean document", encoding="utf-8")
    assert rv.scan_forbidden([good], root=tmp_path) == []


def test_commit_count() -> None:
    assert rv.check_commit_count(225).passed
    assert not rv.check_commit_count(10).passed


def test_tag_readiness() -> None:
    assert rv.tag_is_ready(["v0.0.9"], "v0.1.0")
    assert not rv.tag_is_ready(["v0.1.0"], "v0.1.0")
    assert rv.check_tag_readiness([], "v0.1.0").passed


def test_run_all_returns_named_checks() -> None:
    results = rv.run_all()
    names = {result.name for result in results}
    assert names == {
        "version_consistency",
        "required_docs",
        "required_examples",
        "attribution_scan",
        "commit_count",
        "tag_readiness",
    }


def test_format_report() -> None:
    results = [rv.CheckResult("demo", True, "ok")]
    assert "PASS demo" in rv.format_report(results)
