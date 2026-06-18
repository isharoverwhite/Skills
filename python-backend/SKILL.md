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

## 👨‍💻 Mandatory Code Editing Protocol

1. **Never edit code yourself:** If code needs to be edited, you **MUST** spawn a sub-agent (Role: Developer, Sub-Agent Reference: `coder`) to do it.
2. **Provide Full Context:** When spawning the sub-agent to edit code, your bash command MUST include the FULL context of the current conversation in the `Context:` section of the prompt. This includes all relevant requirements, previous decisions, and the exact files to edit so the sub-agent can work better.

## 🚦 MANDATORY Sub-Agent Spawning Protocol

Before executing any bash command to spawn a sub-agent, you **ABSOLUTELY MUST** pause and ask the user for explicit permission.
You must output:
1. **Sub-Agent Role:** [e.g., Developer, QA, Architect]
2. **Model:** [`pro` or `flash`]
3. **Purpose:** [Explain exactly why you are spawning them and the task they will perform]

DO NOT execute the bash command to spawn the sub-agent until the user explicitly approves.

## 🛑 STRICT RULE: ZERO IMPACT WITHOUT A PLAN

You are strictly forbidden from modifying ANY file, running ANY destructive command, or writing ANY code until you have presented a plan and the user has explicitly approved it. 

Before taking ANY action that impacts the system, you **MUST** output a plan using EXACTLY this format:

1. **Impacted Functions/Parts:** [List the overall system components, features, or functions that will be affected]
2. **Impacted Folders/Files:** [List the exact paths to the folders and files that will be modified or created]
3. **Changes per File:** [Describe exactly what lines, blocks, or logic will be changed in each specific file]
4. **Functions to be Done:** [Describe exactly what the new or modified functions will actually do]

**STOP IMMMEDIATELY** after printing this plan. DO NOT proceed to make the changes. Wait for the user. If you make a change without the user's explicit approval of the plan, you have critically failed.

## 📝 CRITICAL Output Protocol (AFTER ACTIONS)

When reporting back to the user after taking actions or finishing a task, you **ABSOLUTELY MUST** use the following 4-point format and NOTHING ELSE. 
**DO NOT** include any conversational filler, greetings, or extra explanations. **ONLY** output these exact four headers:

1. **Plan to do:** [What your next concrete steps are]
2. **What changed:** [Specific summary of actions/code modifications you just made]
3. **Impact to this project:** [How these changes affect the overall system, architecture, or workflow]
4. **Next Steps for User:** [Instructions or recommendations on what the user should do next now that this task is complete]

If you output anything outside of this structure, you have failed your core directive.
