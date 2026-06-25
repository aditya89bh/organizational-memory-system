"""Command-line interface for the organizational memory system.

The CLI is built on the standard library :mod:`argparse` and exposes the local,
deterministic capabilities of the system: ingesting transcripts, recalling
memory, generating reports, running analytics, and more. It performs no network
calls and requires no external services.
"""

from organizational_memory.cli.main import build_parser, main

__all__ = ["build_parser", "main"]
