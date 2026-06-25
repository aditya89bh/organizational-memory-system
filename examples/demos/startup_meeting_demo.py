"""Runnable startup meeting demo.

Run it with::

    python examples/demos/startup_meeting_demo.py

Ingests a startup standup transcript, extracts decisions, commitments, tasks,
and open loops, persists them in memory, and prints a deterministic follow-up
report. Nothing is left on disk and no network is used.
"""

from organizational_memory.demos.startup import run


def main() -> int:
    for line in run():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
