# Contributing

Thanks for your interest in improving the Organizational Memory System. This
guide covers how to set up your environment, the day-to-day development
workflow, and the commit conventions we follow.

## Prerequisites

- Python 3.11 or newer
- `git`

## Environment setup

Clone the repository and create an isolated virtual environment:

```bash
git clone https://github.com/aditya89bh/organizational-memory-system.git
cd organizational-memory-system
python -m venv .venv
source .venv/bin/activate
```

Install the package together with the development dependencies:

```bash
pip install -e ".[dev]"
```

Optionally enable the git hooks so checks run before each commit:

```bash
pre-commit install
```

## Development workflow

All code must pass linting, type checking, and the test suite before it is
committed. Run the full set of checks locally:

```bash
ruff check .
mypy .
pytest
```

When adding new behavior, include unit tests in the `tests/` directory and keep
the suite green. Public functions and classes should carry clear docstrings, and
all code must be fully type annotated.

## Commit conventions

We use [Conventional Commits](https://www.conventionalcommits.org/) and keep
each commit focused on a single logical change:

- `feat:` a new feature
- `fix:` a bug fix
- `docs:` documentation only changes
- `test:` adding or updating tests
- `build:` build system or dependency changes
- `ci:` continuous integration changes
- `chore:` maintenance tasks

Guidelines:

- One commit per logical change; avoid large catch-all commits.
- Write the subject line in the imperative mood (e.g. "add", not "added").
- Ensure the repository builds and all checks pass after every commit.

## Pull requests

1. Create a topic branch from `main`.
2. Make your changes with accompanying tests and documentation updates.
3. Run `ruff check .`, `mypy .`, and `pytest` and confirm they pass.
4. Open a pull request describing the motivation and the change.
