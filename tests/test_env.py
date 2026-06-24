"""Tests for the environment loader."""

from pathlib import Path

import pytest

from organizational_memory.config import AppConfig
from organizational_memory.env import (
    get_bool_env,
    get_env,
    get_path_env,
    load_config,
)


def test_get_env_returns_default_when_unset() -> None:
    assert get_env("OM_MISSING", "fallback", env={}) == "fallback"


def test_get_bool_env_parses_truthy_values() -> None:
    assert get_bool_env("OM_FLAG", env={"OM_FLAG": "YES"}) is True
    assert get_bool_env("OM_FLAG", env={"OM_FLAG": "off"}) is False


def test_get_bool_env_rejects_invalid_value() -> None:
    with pytest.raises(ValueError, match="not a valid boolean"):
        get_bool_env("OM_FLAG", env={"OM_FLAG": "maybe"})


def test_get_path_env_expands_user() -> None:
    result = get_path_env("OM_DIR", Path("/default"), env={"OM_DIR": "~/data"})
    assert result == Path("~/data").expanduser()


def test_load_config_uses_defaults_for_empty_env() -> None:
    assert load_config(env={}) == AppConfig.default()


def test_load_config_overrides_from_env() -> None:
    config = load_config(env={"OM_DATA_DIR": "/tmp/om", "OM_LOG_LEVEL": "debug"})
    assert config.data_dir == Path("/tmp/om")
    assert config.log_level == "DEBUG"
