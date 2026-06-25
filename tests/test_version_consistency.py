"""Tests that the version 0.1.0 is consistent across the repository."""

import tomllib
from pathlib import Path

from organizational_memory.version import __version__

_REPO_ROOT = Path(__file__).resolve().parents[1]
_EXPECTED = "0.1.0"


def test_version_module() -> None:
    assert __version__ == _EXPECTED


def test_pyproject_version() -> None:
    data = tomllib.loads((_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["version"] == _EXPECTED


def test_readme_version_banner() -> None:
    readme = (_REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert f"Version {_EXPECTED}" in readme


def test_release_notes_exist_for_version() -> None:
    notes = _REPO_ROOT / "docs" / "releases" / f"v{_EXPECTED}.md"
    assert notes.is_file()
    assert f"v{_EXPECTED}" in notes.read_text(encoding="utf-8")
