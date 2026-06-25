"""Package smoke tests: imports and entry points load cleanly."""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]

_PUBLIC_PACKAGES = [
    "organizational_memory",
    "organizational_memory.models",
    "organizational_memory.schemas",
    "organizational_memory.extraction",
    "organizational_memory.storage",
    "organizational_memory.recall",
    "organizational_memory.analytics",
    "organizational_memory.reports",
    "organizational_memory.cli",
    "organizational_memory.observability",
    "organizational_memory.performance",
    "organizational_memory.demos",
    "organizational_memory.utils",
    "organizational_memory.config_validation",
    "organizational_memory.version",
]

_SAFE_SCRIPTS = [
    "verify_package.py",
    "run_release_validation.py",
    "check_coverage.py",
]


def test_top_level_import_exposes_version() -> None:
    module = importlib.import_module("organizational_memory")
    assert module.__version__ == "0.1.0"


@pytest.mark.parametrize("name", _PUBLIC_PACKAGES)
def test_public_package_imports(name: str) -> None:
    assert importlib.import_module(name) is not None


def test_cli_entrypoint_imports() -> None:
    from organizational_memory.cli import build_parser
    from organizational_memory.cli.main import main

    assert callable(build_parser)
    assert callable(main)
    parser = build_parser()
    assert parser.prog


@pytest.mark.parametrize("script", _SAFE_SCRIPTS)
def test_safe_scripts_import(script: str) -> None:
    path = _REPO_ROOT / "scripts" / script
    spec = importlib.util.spec_from_file_location(f"smoke_{script}", path)
    assert spec is not None
    assert spec.loader is not None
    module: Any = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert hasattr(module, "main")
