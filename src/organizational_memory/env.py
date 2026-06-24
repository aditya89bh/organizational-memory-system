"""Environment variable loading utilities.

Reads configuration from the process environment using the ``OM_`` prefix and
builds an :class:`~organizational_memory.config.AppConfig`.
"""

import os
from collections.abc import Mapping
from pathlib import Path

from organizational_memory.config import AppConfig

ENV_PREFIX = "OM_"

_TRUE_VALUES: frozenset[str] = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES: frozenset[str] = frozenset({"0", "false", "no", "off"})


def get_env(
    name: str,
    default: str | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> str | None:
    """Return the raw value of ``name`` from ``env`` or ``default`` if unset."""
    source = os.environ if env is None else env
    return source.get(name, default)


def get_bool_env(
    name: str,
    default: bool = False,
    *,
    env: Mapping[str, str] | None = None,
) -> bool:
    """Return ``name`` parsed as a boolean, or ``default`` if unset.

    Raises:
        ValueError: If the value is set but not a recognized boolean token.
    """
    raw = get_env(name, env=env)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise ValueError(f"Environment variable {name!r} is not a valid boolean: {raw!r}")


def get_path_env(
    name: str,
    default: Path,
    *,
    env: Mapping[str, str] | None = None,
) -> Path:
    """Return ``name`` parsed as a filesystem path, or ``default`` if unset."""
    raw = get_env(name, env=env)
    if raw is None or not raw.strip():
        return default
    return Path(raw).expanduser()


def load_config(env: Mapping[str, str] | None = None) -> AppConfig:
    """Build an :class:`AppConfig` from environment variables.

    Recognized variables (all optional) are ``OM_DATA_DIR``, ``OM_STORAGE_DIR``,
    ``OM_LOG_DIR``, ``OM_LOG_LEVEL``, and ``OM_ENCODING``.
    """
    defaults = AppConfig.default()
    return AppConfig(
        data_dir=get_path_env(f"{ENV_PREFIX}DATA_DIR", defaults.data_dir, env=env),
        storage_dir=get_path_env(
            f"{ENV_PREFIX}STORAGE_DIR", defaults.storage_dir, env=env
        ),
        log_dir=get_path_env(f"{ENV_PREFIX}LOG_DIR", defaults.log_dir, env=env),
        log_level=(
            get_env(f"{ENV_PREFIX}LOG_LEVEL", defaults.log_level, env=env) or ""
        ).upper(),
        encoding=get_env(f"{ENV_PREFIX}ENCODING", defaults.encoding, env=env)
        or defaults.encoding,
    )
