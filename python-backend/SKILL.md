---
name: python-backend
description: "Build and maintain modern Python backends with FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, pytest, ruff, and uv. Use when working on Python APIs, async services, backend data models, request or response validation, migrations, background jobs, or backend test suites."
---

# Python Backend

Use this skill for implementation work in Python backend services. Read the repository's existing structure first and preserve it unless the task explicitly requires a larger refactor.

## Default stack

Prefer these defaults when the repository does not already establish a different backend pattern:

- FastAPI for HTTP APIs and dependency wiring
- Pydantic v2 for transport schemas and settings
- SQLAlchemy 2.x for persistence
- Alembic for schema migrations
- `uv` for dependency and command execution
- `ruff` for linting and formatting
- `pytest` for tests

## Workflow

1. Inspect the entrypoints, settings, dependency injection, persistence layer, and current test patterns before editing.
2. Trace the change end to end across router, service, repository, jobs, and integrations.
3. Keep handlers thin and move business rules into service or domain modules.
4. Validate at the boundary with explicit request and response models.
5. Apply the smallest safe schema or persistence change that satisfies the task.
6. Add or update focused tests before broadening verification.
7. Run the narrowest useful checks first, then expand if the change touches shared behavior.

## API guidance

- Use typed request and response models.
- Declare status codes, failure modes, and auth dependencies explicitly.
- Raise framework or project error types instead of returning ad hoc error dictionaries.
- Use async endpoints only when downstream work is genuinely async or I/O bound.
- Keep serialization predictable; do not leak ORM entities directly unless the project already relies on that pattern.

## Persistence guidance

- Use SQLAlchemy 2.x style APIs such as `select()` and `session.execute()`.
- Choose `scalar_one()`, `scalar_one_or_none()`, `scalars()`, or `mappings()` based on the expected result shape.
- Keep transaction boundaries explicit and commit once per unit of work.
- Avoid accidental lazy loading in hot paths when eager loading is clearer.
- When schema changes are required, add the repository-native Alembic migration and verify upgrade and downgrade paths if the project expects both.

## Schema and validation guidance

- Prefer `model_validate()` and `model_dump()` over deprecated Pydantic v1 patterns.
- Keep transport schemas separate from ORM models unless the codebase intentionally combines them.
- Use validators to protect real invariants, not cosmetic transformations that belong elsewhere.
- Be deliberate with optional fields, defaults, and partial update semantics.

## Testing and tooling

- Use `uv run` when the repository uses `uv`.
- Reuse existing fixtures, factories, and markers before creating new ones.
- Run targeted `pytest` coverage for the changed path.
- Run `ruff check` on touched files and formatting checks when configured.
- Add broader integration or API checks only when the change crosses module boundaries.

## Avoid

- Mixing sync database access into async request paths without understanding the runtime impact.
- Refactoring unrelated modules while fixing a narrow backend bug or feature.
- Adding new frameworks or dependencies when the existing stack already solves the problem.
- Writing skill boilerplate, setup guides, or user-facing docs that do not help another agent execute backend work.

## Completion

When finishing work, report three things: what changed, what you verified, and any remaining risk or untested edge case.

## 📝 CRITICAL Output Protocol (MANDATORY)

When you report back to the user, you **ABSOLUTELY MUST** use the following 3-point format and NOTHING ELSE. 
**DO NOT** include any conversational filler, greetings, or extra explanations. **ONLY** output these exact three headers:

1. **Plan to do:** [Your next concrete steps]
2. **What changed:** [Specific summary of actions/code modifications made]
3. **Impact to this project:** [How this affects the overall system, architecture, or workflow]

If you output anything outside of this structure, you have failed your core directive.
