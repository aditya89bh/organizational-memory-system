"""Runnable organizational timeline demo.

Run it with::

    python examples/demos/organizational_timeline_demo.py

Ingests multiple meetings spread over time, then prints deterministic timeline
analytics and a timeline report showing chronological activity. Nothing is left
on disk and no network is used.
"""

from organizational_memory.demos.timeline import run


def main() -> int:
    for line in run():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
