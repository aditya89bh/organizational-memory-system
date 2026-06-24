"""Tests for version management."""

from importlib import metadata

import organizational_memory
from organizational_memory.version import __version__


def test_version_is_non_empty_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_package_reexports_version() -> None:
    assert organizational_memory.__version__ == __version__


def test_version_matches_distribution_metadata() -> None:
    assert metadata.version("organizational-memory") == __version__
