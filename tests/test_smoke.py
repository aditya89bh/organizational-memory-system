"""Smoke tests verifying the package imports and basic wiring works."""

import organizational_memory
from organizational_memory.config import AppConfig


def test_package_exposes_version() -> None:
    assert organizational_memory.__version__


def test_app_config_fixture_is_isolated(app_config: AppConfig) -> None:
    assert app_config.storage_dir.parent == app_config.data_dir
    assert app_config.log_level == "INFO"
