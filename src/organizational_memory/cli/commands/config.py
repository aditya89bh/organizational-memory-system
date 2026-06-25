"""``config`` command: manage local CLI configuration."""

import argparse
from pathlib import Path

from organizational_memory.cli.common import BACKENDS
from organizational_memory.cli.config_file import (
    DEFAULT_CONFIG_PATH,
    CLIConfig,
    load_config,
    save_config,
)
from organizational_memory.config import AppConfig


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``config`` subcommand."""
    parser = subparsers.add_parser(
        "config",
        help="Show, initialize, validate, or update local configuration.",
        description="Manage the local, deterministic CLI configuration file.",
    )
    parser.add_argument(
        "action",
        choices=("show", "init", "validate", "set-store"),
        help="Configuration action to run.",
    )
    parser.add_argument(
        "--path", default=DEFAULT_CONFIG_PATH,
        help="Config file path (default: %(default)s).",
    )
    parser.add_argument("--store", default=None, help="Store path for set-store.")
    parser.add_argument(
        "--backend", choices=BACKENDS, default=None, help="Backend for set-store."
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing config on init."
    )
    parser.set_defaults(handler=run)


def _show_defaults() -> int:
    app = AppConfig.default()
    cli = CLIConfig()
    print("Application defaults")
    print(f"  data_dir: {app.data_dir}")
    print(f"  storage_dir: {app.storage_dir}")
    print(f"  log_dir: {app.log_dir}")
    print(f"  log_level: {app.log_level}")
    print(f"  encoding: {app.encoding}")
    print("CLI defaults")
    print(f"  store: {cli.store}")
    print(f"  backend: {cli.backend}")
    return 0


def _init(path: str, force: bool) -> int:
    if Path(path).exists() and not force:
        print(f"error: {path} already exists (use --force to overwrite)")
        return 1
    save_config(path, CLIConfig())
    print(f"Wrote {path}")
    return 0


def _validate(path: str) -> int:
    try:
        config = load_config(path)
    except ValueError as error:
        print(f"invalid: {error}")
        return 1
    print(f"valid: store={config.store} backend={config.backend}")
    return 0


def _set_store(path: str, store: str | None, backend: str | None) -> int:
    if store is None and backend is None:
        print("error: provide --store and/or --backend")
        return 1
    current = load_config(path) if Path(path).exists() else CLIConfig()
    updated = CLIConfig(
        store=store if store is not None else current.store,
        backend=backend if backend is not None else current.backend,
    )
    save_config(path, updated)
    print(f"Wrote {path}")
    return 0


def run(args: argparse.Namespace) -> int:
    """Execute the ``config`` command."""
    if args.action == "show":
        return _show_defaults()
    if args.action == "init":
        return _init(args.path, args.force)
    if args.action == "validate":
        return _validate(args.path)
    try:
        return _set_store(args.path, args.store, args.backend)
    except ValueError as error:
        print(f"error: {error}")
        return 1
