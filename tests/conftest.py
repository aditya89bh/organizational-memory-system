"""Shared pytest fixtures."""

from pathlib import Path

import pytest

from organizational_memory.config import AppConfig


@pytest.fixture
def app_config(tmp_path: Path) -> AppConfig:
    """Return an :class:`AppConfig` rooted at an isolated temporary directory."""
    return AppConfig(
        data_dir=tmp_path,
        storage_dir=tmp_path / "storage",
        log_dir=tmp_path / "logs",
    )
