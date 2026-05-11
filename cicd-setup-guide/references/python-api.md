# Python, FastAPI, and Django

Use this file when the repository is Python based.

## Detect the Toolchain

Look for these signals:

- `pyproject.toml`
- `uv.lock`
- `poetry.lock`
- `requirements.txt` or split requirements files
- `manage.py` for Django
- `alembic.ini` for SQLAlchemy and Alembic workflows

## Standard Tasks

Prefer repositories that expose or document these tasks:

- Dependency install
- Lint, often with Ruff
- Test, often with Pytest
- Optional typecheck with mypy or pyright
- Build or container packaging if the app is distributed

## Install Rules

| Signal | Install command | Notes |
|---|---|---|
| `uv.lock` | `uv sync --frozen --all-extras --dev` | Prefer `uv run` for commands |
| `poetry.lock` | `poetry install --no-interaction` | Use repo conventions for virtualenvs |
| `requirements.txt` | `python -m pip install -r requirements.txt` | Install dev requirements if tests need them |

## CI Order

Use this order when the repository supports it:

1. Install dependencies
2. Run lint
3. Run tests
4. Run typecheck if configured
5. Build package or container if release logic depends on it

## FastAPI Notes

- Prefer a health endpoint for deployment validation
- Include Alembic migration checks only if the repo already uses Alembic
- Prefer container delivery when the hosting target is not obvious

## Django Notes

- Consider `python manage.py check` if the repo uses Django
- Handle `collectstatic` only in the deploy or image build path, not every CI job
- Call out migration expectations when release safety depends on them

## Common File Gaps

Recommend or verify these files when they are missing:

- `.python-version` or explicit Python version in CI
- `.env.example`
- `pytest.ini`, `pyproject.toml` test config, or equivalent
- `Dockerfile` if deployment requires a container contract

## Template

Start from `assets/github-actions/python-ci.yml` for the default CI path.
