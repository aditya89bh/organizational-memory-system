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

## Testing commands

The core quality gate is `ruff check .`, `mypy .`, and `pytest`. Additional
local tooling is available:

```bash
# Coverage (writes coverage.json) and the coverage gate
pytest --cov --cov-report=json
python scripts/check_coverage.py --coverage-file coverage.json --min 80

# Benchmarks (informational; no hard timing thresholds)
python scripts/run_performance_benchmarks.py
python scripts/run_memory_benchmarks.py
python scripts/run_load_tests.py
python scripts/run_stress_tests.py

# Package verification
python scripts/verify_package.py
```

See [docs/testing.md](docs/testing.md) for details on coverage configuration.

## Release validation

Before proposing a release, confirm `tests/test_release_validation.py` passes.
It checks that the package imports, the CLI entry point exists, key docs and
examples are present, the declared version is consistent, and no forbidden
attribution strings appear in tracked text files.

```bash
pytest tests/test_release_validation.py
python scripts/verify_package.py
```

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

### Attribution rules

- Do **not** add co-author trailers or any automated tool attribution to commit
  messages, commit metadata, code comments, docs, or examples.
- Author and committer identity must be a real human contributor.
- The release validation test enforces that tracked text files contain no
  generated-tool attribution strings.

## Documentation expectations

- Update documentation only for features that actually exist; do not describe
  unimplemented behavior.
- Keep the `README.md` accurate and in sync with the CLI and library.
- Be explicit that this is a local, deterministic toolkit. Do not overclaim
  production readiness; see
  [docs/production_readiness.md](docs/production_readiness.md).
- When you add a user-facing capability, update the relevant guide under `docs/`
  and the [changelog](CHANGELOG.md).

## Pull requests

1. Create a topic branch from `main`.
2. Make your changes with accompanying tests and documentation updates.
3. Run `ruff check .`, `mypy .`, and `pytest` and confirm they pass.
4. Open a pull request describing the motivation and the change.
