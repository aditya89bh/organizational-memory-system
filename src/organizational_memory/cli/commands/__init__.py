"""CLI subcommand registration.

Each command module exposes a ``register(subparsers)`` function. ``register_all``
wires every command into the top-level parser, keeping :mod:`cli.main` thin.
"""

import argparse

from organizational_memory.cli.commands import (
    analytics,
    commitments,
    config,
    demo,
    export,
    ingest,
    open_loops,
    recall,
    report,
)


def register_all(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register every CLI subcommand onto ``subparsers``."""
    ingest.register(subparsers)
    recall.register(subparsers)
    report.register(subparsers)
    analytics.register(subparsers)
    commitments.register(subparsers)
    open_loops.register(subparsers)
    export.register(subparsers)
    config.register(subparsers)
    demo.register(subparsers)
