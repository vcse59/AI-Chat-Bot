# Contributing

Thanks for wanting to contribute! This document covers a short PR template, code style rules, and how to run checks locally.

## Pull request checklist

- Fork the repository and create a branch named `feat/<short-desc>`, `fix/<short-desc>` or `chore/<short-desc>`.
- Add tests for new features or bug fixes where applicable.
- Keep changes small and focused.
- Ensure the CI checks pass before requesting review.

## PR template (summary)

Title: [TYPE] Short description

Description:
- What this change does
- Why it is needed
- Any side-effects or migration notes

Related issues: # (if applicable)

Checklist:
- [ ] Tests added
- [ ] Documentation updated (README or docs)
- [ ] Linting/formatting applied

## Code style

We follow a small set of rules to keep the codebase consistent:

- Formatting: use `black` (opinionated formatting).
- Linting: use `flake8` to catch common issues. Aim to keep `E` and `F` errors fixed; `W`/`C`/`D` are advisory.
- Type hints: prefer explicit typing for public functions and models. Use `mypy` in CI if enabled.
- Tests: use `pytest` for unit tests. Keep tests fast and focused.

Example commands (assuming Poetry-managed environment):

```cmd
poetry install
poetry run black --check .
poetry run flake8
poetry run pytest -q
```

## Files to update in PRs

- If you add a new Python module, include tests under the `tests/` directory.
- Update `README.md` or subproject READMEs for user-facing changes.

## How to propose larger design changes

If you plan to change architecture or public APIs, open an issue first describing the proposal and solicit feedback before implementing.

## Repository overview

This repository is a monorepo for authentication, authorization, and security modules. The primary subproject is the `Authentication-Authorization` service. For user-facing docs and run instructions, see `Authentication-Authorization/README.md`.

## Pre-commit (optional, recommended)

We recommend using `pre-commit` to run linters and formatters locally before committing. Install and enable hooks with:

```cmd
poetry install
poetry run pre-commit install
poetry run pre-commit run --all-files
```

Add this to your local setup steps to avoid common style/linting failures in CI.
