"""Smoke checks that coverage reporting is configured."""

import tomllib
from pathlib import Path

_PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def _config() -> dict[str, object]:
    return tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))


def test_pytest_cov_is_a_dev_dependency() -> None:
    config = _config()
    project = config["project"]
    assert isinstance(project, dict)
    optional = project["optional-dependencies"]
    assert isinstance(optional, dict)
    dev = optional["dev"]
    assert any("pytest-cov" in dependency for dependency in dev)


def test_coverage_run_is_scoped_to_package() -> None:
    tool = _config()["tool"]
    assert isinstance(tool, dict)
    coverage = tool["coverage"]
    assert isinstance(coverage, dict)
    run = coverage["run"]
    assert isinstance(run, dict)
    assert "organizational_memory" in run["source"]
    assert run["branch"] is True


def test_coverage_json_output_configured() -> None:
    tool = _config()["tool"]
    assert isinstance(tool, dict)
    coverage = tool["coverage"]
    assert isinstance(coverage, dict)
    assert coverage["json"]["output"] == "coverage.json"
