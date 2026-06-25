"""Shared helpers for CLI commands.

Centralizes store selection (JSON or SQLite), common argument groups, and
output handling so every command behaves consistently and deterministically.
"""

import argparse
from pathlib import Path

from organizational_memory.constants import ENCODING
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.sqlite_store import SQLiteStore
from organizational_memory.storage.store import MemoryStore

DEFAULT_STORE_PATH = "memory.json"
BACKENDS = ("json", "sqlite")


def add_store_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the shared ``--store`` and ``--backend`` options to ``parser``."""
    parser.add_argument(
        "--store",
        default=DEFAULT_STORE_PATH,
        help="Path to the memory store file (default: %(default)s).",
    )
    parser.add_argument(
        "--backend",
        choices=BACKENDS,
        default="json",
        help="Storage backend to use (default: %(default)s).",
    )


def open_store(path: str, backend: str) -> MemoryStore:
    """Open (or create) a memory store of ``backend`` at ``path``."""
    if backend == "sqlite":
        return SQLiteStore(path)
    return JSONStore(path)


def open_store_from_args(args: argparse.Namespace) -> MemoryStore:
    """Open a store using the standard ``--store``/``--backend`` arguments."""
    return open_store(args.store, args.backend)


def write_output(text: str, path: str | None) -> None:
    """Print ``text`` to stdout, or write it to ``path`` and confirm."""
    if path is None:
        print(text)
        return
    payload = text if text.endswith("\n") else text + "\n"
    Path(path).write_text(payload, encoding=ENCODING)
    print(f"Wrote {path}")
