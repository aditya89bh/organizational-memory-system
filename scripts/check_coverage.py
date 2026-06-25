"""Deterministic coverage gate.

Parses a coverage report (JSON from ``coverage json`` or the plain-text
``coverage report`` output) and checks the total line coverage against a
configurable minimum threshold. Prints a clear pass/fail message and exits
non-zero on failure.

Usage::

    python scripts/check_coverage.py --coverage-file coverage.json --min 85
    coverage report | python scripts/check_coverage.py --format text --min 85
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

DEFAULT_THRESHOLD = 80.0
_TEXT_TOTAL_RE = re.compile(r"^TOTAL\s+.*?(\d+(?:\.\d+)?)%\s*$", re.MULTILINE)


def parse_coverage_json(data: dict[str, Any]) -> float:
    """Return the total percent covered from a coverage.py JSON document."""
    try:
        totals = data["totals"]
        return float(totals["percent_covered"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"invalid coverage JSON: {error}") from error


def parse_coverage_text(text: str) -> float:
    """Return the total percent covered from ``coverage report`` text output."""
    matches = list(_TEXT_TOTAL_RE.finditer(text))
    if not matches:
        raise ValueError("could not find a TOTAL line in coverage text output")
    return float(matches[-1].group(1))


def evaluate(percent: float, threshold: float) -> tuple[bool, str]:
    """Return whether ``percent`` meets ``threshold`` and a human-readable message."""
    passed = percent >= threshold
    status = "PASS" if passed else "FAIL"
    return passed, (
        f"{status}: coverage {percent:.2f}% (threshold {threshold:.2f}%)"
    )


def _read_percent(args: argparse.Namespace) -> float:
    if args.format == "json":
        if args.coverage_file == "-":
            raw = sys.stdin.read()
        else:
            with open(args.coverage_file, encoding="utf-8") as handle:
                raw = handle.read()
        return parse_coverage_json(json.loads(raw))
    if args.coverage_file == "-":
        return parse_coverage_text(sys.stdin.read())
    with open(args.coverage_file, encoding="utf-8") as handle:
        return parse_coverage_text(handle.read())


def main(argv: list[str] | None = None) -> int:
    """Run the coverage gate and return a process exit code."""
    parser = argparse.ArgumentParser(description="Coverage gate.")
    parser.add_argument("--coverage-file", default="coverage.json")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument(
        "--min", dest="threshold", type=float, default=DEFAULT_THRESHOLD
    )
    args = parser.parse_args(argv)

    try:
        percent = _read_percent(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}")
        return 2

    passed, message = evaluate(percent, args.threshold)
    print(message)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
