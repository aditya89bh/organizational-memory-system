"""Bundled, deterministic demos of the full organizational memory pipeline.

Each demo runs entirely in memory and returns a list of output lines. Demos are
reproducible: identifiers and timestamps are stabilized so output never changes
between runs.
"""

from collections.abc import Callable

from organizational_memory.demos import (
    board,
    company_memory,
    sprint,
    startup,
    timeline,
)

DemoFn = Callable[[], list[str]]

DEMOS: dict[str, DemoFn] = {
    "startup": startup.run,
    "sprint": sprint.run,
    "board": board.run,
    "timeline": timeline.run,
    "company-memory": company_memory.run,
}


def available_demos() -> list[str]:
    """Return the demo names in their canonical display order."""
    return list(DEMOS)


def run_demo(name: str) -> list[str]:
    """Run the demo named ``name`` and return its output lines."""
    try:
        demo = DEMOS[name]
    except KeyError as error:
        raise ValueError(f"unknown demo: {name}") from error
    return demo()


def run_all() -> list[str]:
    """Run every demo and return the combined output lines."""
    lines: list[str] = []
    for index, name in enumerate(DEMOS):
        if index:
            lines.append("")
        lines.extend(DEMOS[name]())
    return lines


__all__ = ["DEMOS", "available_demos", "run_all", "run_demo"]
