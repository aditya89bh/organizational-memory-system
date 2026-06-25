"""Runnable analytics report example.

Run it with::

    python examples/analytics/analytics_report_example.py

Loads the committed analytics benchmark snapshot and prints a structured
analytics report and dashboard snapshot at a fixed reference time. Read-only.
"""

import json
from pathlib import Path

from organizational_memory.analytics.reporting import (
    build_dashboard_snapshot,
    generate_report,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp

FIXTURES = Path(__file__).resolve().parent
NOW = parse_timestamp("2026-03-01T00:00:00Z")


def main() -> int:
    store = JSONStore(FIXTURES / "analytics_memory_snapshot.json")

    report = generate_report(store, now=NOW)
    print("Summary:")
    for key, value in report.summary.items():
        print(f"  - {key}: {value}")
    print("Key metrics:")
    for key, value in report.key_metrics.items():
        print(f"  - {key}: {value}")
    print(f"Risks: {len(report.risks)}")
    print("Recommendations:")
    for recommendation in report.recommendations:
        print(f"  - {recommendation}")

    snapshot = build_dashboard_snapshot(store, now=NOW)
    print("\nDashboard snapshot (JSON):")
    print(json.dumps(snapshot.to_dict(), indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
