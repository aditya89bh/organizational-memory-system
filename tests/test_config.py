"""Tests for configuration models."""

from pathlib import Path

import pytest

from organizational_memory import constants
from organizational_memory.config import AppConfig


def test_default_config_uses_constants() -> None:
    config = AppConfig.default()
    assert config.data_dir == constants.DEFAULT_DATA_DIR
    assert config.encoding == constants.ENCODING
    assert config.log_level == "INFO"


def test_config_is_immutable() -> None:
    config = AppConfig.default()
    with pytest.raises(AttributeError):
        config.log_level = "DEBUG"  # type: ignore[misc]


def test_invalid_log_level_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid log level"):
        AppConfig(log_level="VERBOSE")


def test_custom_paths_are_preserved() -> None:
    config = AppConfig(data_dir=Path("/tmp/om"))
    assert config.data_dir == Path("/tmp/om")
