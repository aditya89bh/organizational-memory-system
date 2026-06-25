"""Runnable board meeting demo.

Run it with::

    python examples/demos/board_meeting_demo.py

Ingests a board review transcript, extracts decisions and risks, and prints a
deterministic decision report and organizational memory report. Nothing is left
on disk and no network is used.
"""

from organizational_memory.demos.board import run


def main() -> int:
    for line in run():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
