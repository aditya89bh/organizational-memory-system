"""Package verification checks for release readiness.

Runs a set of fast, deterministic checks that the package is importable, exposes
its CLI entry point and version, ships its bundled examples and key docs, and has
the expected ``pyproject.toml`` metadata. Each check returns a
:class:`CheckResult`; the script exits non-zero if any check fails.

Usage::

    python scripts/verify_package.py
"""

from __future__ import annotations

import importlib
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]

_CORE_MODULES = (
    "organizational_memory",
    "organizational_memory.models",
    "organizational_memory.extraction.pipeline",
    "organizational_memory.storage.json_store",
    "organizational_memory.recall.keyword_search",
    "organizational_memory.analytics.reporting",
    "organizational_memory.reports.base",
    "organizational_memory.cli.main",
)

_EXAMPLE_FILES = (
    "examples/demos/startup_meeting_demo.py",
    "examples/demos/sprint_planning_demo.py",
    "examples/demos/board_meeting_demo.py",
    "examples/datasets/startup_operating_memory.json",
    "examples/datasets/company_memory_full.json",
)

_DOC_FILES = (
    "README.md",
    "docs/user_guide.md",
    "docs/testing.md",
    "docs/demos.md",
    "docs/interactive_walkthrough.md",
)


@dataclass(frozen=True)
class CheckResult:
    """The outcome of a single verification check."""

    name: str
    passed: bool
    detail: str


def check_imports() -> CheckResult:
    """Verify the core modules import cleanly."""
    for name in _CORE_MODULES:
        try:
            importlib.import_module(name)
        except ImportError as error:
            return CheckResult("imports", False, f"failed to import {name}: {error}")
    return CheckResult("imports", True, f"imported {len(_CORE_MODULES)} modules")


def check_cli_entrypoint() -> CheckResult:
    """Verify the CLI exposes ``build_parser`` and ``main``."""
    module = importlib.import_module("organizational_memory.cli.main")
    has_parser = callable(getattr(module, "build_parser", None))
    has_main = callable(getattr(module, "main", None))
    passed = has_parser and has_main
    return CheckResult(
        "cli_entrypoint", passed, f"build_parser={has_parser} main={has_main}"
    )


def check_version() -> CheckResult:
    """Verify a non-empty package version is available."""
    module = importlib.import_module("organizational_memory.version")
    version = getattr(module, "__version__", "")
    passed = isinstance(version, str) and bool(version.strip())
    return CheckResult("version", passed, f"version={version!r}")


def check_examples(root: Path = _REPO_ROOT) -> CheckResult:
    """Verify bundled example files exist."""
    missing = [name for name in _EXAMPLE_FILES if not (root / name).is_file()]
    if missing:
        return CheckResult("examples", False, f"missing: {missing}")
    return CheckResult("examples", True, f"found {len(_EXAMPLE_FILES)} examples")


def check_docs(root: Path = _REPO_ROOT) -> CheckResult:
    """Verify key documentation files exist."""
    missing = [name for name in _DOC_FILES if not (root / name).is_file()]
    if missing:
        return CheckResult("docs", False, f"missing: {missing}")
    return CheckResult("docs", True, f"found {len(_DOC_FILES)} docs")


def check_pyproject_metadata(root: Path = _REPO_ROOT) -> CheckResult:
    """Verify required ``pyproject.toml`` metadata is present."""
    path = root / "pyproject.toml"
    if not path.is_file():
        return CheckResult("pyproject", False, "pyproject.toml not found")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    project = data.get("project", {})
    has_name = bool(project.get("name"))
    has_version = bool(project.get("version"))
    scripts = project.get("scripts", {})
    has_script = "organizational-memory" in scripts
    passed = has_name and has_version and has_script
    return CheckResult(
        "pyproject",
        passed,
        f"name={has_name} version={has_version} script={has_script}",
    )


def run_all(root: Path = _REPO_ROOT) -> list[CheckResult]:
    """Run every verification check and return the results."""
    return [
        check_imports(),
        check_cli_entrypoint(),
        check_version(),
        check_examples(root),
        check_docs(root),
        check_pyproject_metadata(root),
    ]


def format_report(results: list[CheckResult]) -> str:
    """Build a human-readable verification report."""
    lines = ["Package verification", ""]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"  {status} {result.name}: {result.detail}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Run all package verification checks and print a report."""
    results = run_all()
    print(format_report(results))
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
