"""``demo`` command: run bundled, deterministic pipeline demos."""

import argparse

from organizational_memory.demos import available_demos, run_all, run_demo


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``demo`` subcommand."""
    parser = subparsers.add_parser(
        "demo",
        help="Run a bundled, deterministic demo.",
        description="Run a demo of the full pipeline using bundled examples.",
    )
    parser.add_argument(
        "name",
        choices=(*available_demos(), "all"),
        help="Demo to run, or 'all' for every demo.",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    """Execute the ``demo`` command."""
    lines = run_all() if args.name == "all" else run_demo(args.name)
    for line in lines:
        print(line)
    return 0
