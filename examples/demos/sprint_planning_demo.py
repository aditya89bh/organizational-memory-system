"""Runnable sprint planning demo.

Run it with::

    python examples/demos/sprint_planning_demo.py

Ingests sprint planning notes, identifies tasks and commitments, detects
blockers (dependencies) and open loops, and prints a deterministic weekly
report. Nothing is left on disk and no network is used.
"""

from organizational_memory.demos.sprint import run


def main() -> int:
    for line in run():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
