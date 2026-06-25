"""CLI subcommand registration.

Each command module exposes a ``register(subparsers)`` function. ``register_all``
wires every command into the top-level parser, keeping :mod:`cli.main` thin.
"""

import argparse

from organizational_memory.cli.commands import ingest


def register_all(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register every CLI subcommand onto ``subparsers``."""
    ingest.register(subparsers)
