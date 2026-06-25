"""Local, deterministic CLI configuration file handling.

The CLI configuration is a small JSON document describing the default store
path and backend. It is entirely local: no network access, no environment
inspection beyond the provided file path.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from organizational_memory.cli.common import BACKENDS, DEFAULT_STORE_PATH
from organizational_memory.constants import ENCODING

DEFAULT_CONFIG_PATH = "organizational_memory.config.json"


@dataclass(frozen=True)
class CLIConfig:
    """Local CLI configuration."""

    store: str = DEFAULT_STORE_PATH
    backend: str = "json"

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable mapping of the configuration."""
        return asdict(self)


def _validate(data: dict[str, object]) -> CLIConfig:
    store = data.get("store", DEFAULT_STORE_PATH)
    backend = data.get("backend", "json")
    if not isinstance(store, str) or not store:
        raise ValueError("'store' must be a non-empty string")
    if not isinstance(backend, str) or backend not in BACKENDS:
        raise ValueError(f"'backend' must be one of {sorted(BACKENDS)}")
    return CLIConfig(store=store, backend=backend)


def load_config(path: str | Path) -> CLIConfig:
    """Load and validate a :class:`CLIConfig` from ``path``."""
    file_path = Path(path)
    try:
        raw = file_path.read_text(encoding=ENCODING)
    except OSError as error:
        raise ValueError(f"cannot read config file: {file_path}") from error
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in config file: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("config file must contain a JSON object")
    return _validate(data)


def save_config(path: str | Path, config: CLIConfig) -> None:
    """Write ``config`` to ``path`` as deterministic, sorted JSON."""
    payload = json.dumps(config.to_dict(), indent=2, sort_keys=True)
    Path(path).write_text(payload + "\n", encoding=ENCODING)
