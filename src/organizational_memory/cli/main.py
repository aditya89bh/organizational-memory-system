"""CLI entry point and argument parser construction.

``build_parser`` assembles the top-level parser and registers every subcommand.
``main`` parses arguments and dispatches to the selected command's handler,
returning a process exit code. Running with no subcommand prints help and exits
cleanly.
"""

import argparse
from collections.abc import Sequence

from organizational_memory.version import __version__

_PROG = "organizational-memory"
_DESCRIPTION = (
    "Local, deterministic organizational memory: ingest transcripts, recall "
    "memory, run analytics, and generate reports. No network calls."
)


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser with all subcommands registered."""
    parser = argparse.ArgumentParser(prog=_PROG, description=_DESCRIPTION)
    parser.add_argument(
        "--version",
        action="version",
        version=f"{_PROG} {__version__}",
    )
    parser.add_subparsers(dest="command", metavar="<command>")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse ``argv`` and dispatch to the selected command.

    Returns a process exit code: ``0`` on success (including when no command is
    given, in which case help is printed), or a command-specific non-zero code.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0
    exit_code = handler(args)
    return int(exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
