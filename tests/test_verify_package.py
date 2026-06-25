"""Tests for the package verification helpers."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_package.py"


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("verify_package", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


vp = _load()


def test_check_imports() -> None:
    assert vp.check_imports().passed


def test_check_cli_entrypoint() -> None:
    assert vp.check_cli_entrypoint().passed


def test_check_version() -> None:
    result = vp.check_version()
    assert result.passed


def test_check_examples() -> None:
    assert vp.check_examples().passed


def test_check_docs() -> None:
    assert vp.check_docs().passed


def test_check_pyproject_metadata() -> None:
    assert vp.check_pyproject_metadata().passed


def test_examples_missing_in_empty_root(tmp_path: Path) -> None:
    assert not vp.check_examples(tmp_path).passed


def test_docs_missing_in_empty_root(tmp_path: Path) -> None:
    assert not vp.check_docs(tmp_path).passed


def test_pyproject_missing_in_empty_root(tmp_path: Path) -> None:
    assert not vp.check_pyproject_metadata(tmp_path).passed


def test_run_all_passes() -> None:
    results = vp.run_all()
    assert all(result.passed for result in results)
    assert len(results) == 6


def test_main() -> None:
    assert vp.main() == 0


def test_format_report() -> None:
    text = vp.format_report(vp.run_all())
    assert "Package verification" in text
    assert "PASS" in text
