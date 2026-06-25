"""Runnable company memory demo.

Run it with::

    python examples/demos/company_memory_demo.py

Answers deterministic questions against the persisted memory using recall and
reports:

- Why did we delay the launch?
- Who owns the website redesign?
- What is still unresolved?
- What is overdue?

Nothing is left on disk and no network is used.
"""

from organizational_memory.demos.company_memory import run


def main() -> int:
    for line in run():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
