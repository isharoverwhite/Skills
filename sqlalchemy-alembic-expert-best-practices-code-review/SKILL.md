---
name: sqlalchemy-alembic-expert-best-practices-code-review
description: SQLAlchemy ORM and Alembic migration best practices for building safe, performant database schemas. This skill should be used when writing, reviewing, or refactoring SQLAlchemy models, Alembic migrations, or database query patterns. Triggers on tasks involving SQLAlchemy ORM, Alembic migrations, database schema changes, or query optimization.
license: MIT
metadata:
  author: wispbit
  version: "1.0.0"
---

# SQLAlchemy & Alembic Expert Best Practices

Simple, pragmatic, opinionated. Only what matters for writing production-grade SQLAlchemy and Alembic code.

## When to Apply

Reference these guidelines when:
- Writing Alembic migrations for schema changes
- Creating or modifying SQLAlchemy models
- Adding indexes, constraints, or foreign keys via Alembic
- Reviewing database migration code for safety
- Refactoring existing database schemas
- Optimizing query patterns or database performance

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Index Management | CRITICAL-HIGH | `only-concurrent-indexes`, `verify-query-patterns-are-indexed` |
| 2 | Constraint Safety | HIGH | `unique-constraint`, `split-foreign-key`, `change-column-type` |
| 3 | Optimization | MEDIUM | `split-check-constraint`, `limit-non-unique-index` |
| 4 | Index Efficiency | LOW | `ensure-index-not-covered` |

## Quick Reference

- `only-concurrent-indexes` - Always use `postgresql_concurrently=True` with autocommit blocks for index operations
- `verify-query-patterns-are-indexed` - Ensure SQLAlchemy queries have appropriate indexes defined
- `unique-constraint` - Split unique constraint creation into concurrent index + constraint steps
- `split-foreign-key` - Add foreign keys with `NOT VALID` first, then validate separately
- `change-column-type` - Use multi-step approach for column type changes to avoid table locks
- `split-check-constraint` - Add check constraints with `NOT VALID` first, then validate separately
- `limit-non-unique-index` - Limit non-unique indexes to maximum three columns for efficiency
- `ensure-index-not-covered` - Prevent redundant indexes that are already covered by composite indexes

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/only-concurrent-indexes.md
rules/verify-query-patterns-are-indexed.md
rules/unique-constraint.md
rules/split-foreign-key.md
rules/change-column-type.md
rules/split-check-constraint.md
rules/limit-non-unique-index.md
rules/ensure-index-not-covered.md
```

Each rule file contains:
- Brief explanation of why it matters
- Impact level and description
- Incorrect SQLAlchemy/Alembic example with explanation
- Correct implementation with best practices
- Additional context for safe migrations

## 🛑 STRICT RULE: ZERO IMPACT WITHOUT A PLAN

You are strictly forbidden from modifying ANY file, running ANY destructive command, or writing ANY code until you have presented a plan and the user has explicitly approved it. 

Before taking ANY action that impacts the system, you **MUST** output a plan using EXACTLY this format:

1. **Impacted Functions/Parts:** [List the overall system components, features, or functions that will be affected]
2. **Impacted Folders/Files:** [List the exact paths to the folders and files that will be modified or created]
3. **Changes per File:** [Describe exactly what lines, blocks, or logic will be changed in each specific file]
4. **Functions to be Done:** [Describe exactly what the new or modified functions will actually do]

**STOP IMMMEDIATELY** after printing this plan. DO NOT proceed to make the changes. Wait for the user. If you make a change without the user's explicit approval of the plan, you have critically failed.

## 📝 CRITICAL Output Protocol (AFTER ACTIONS)

When reporting back to the user after taking actions or finishing a task, you **ABSOLUTELY MUST** use the following 3-point format and NOTHING ELSE. 
**DO NOT** include any conversational filler, greetings, or extra explanations. **ONLY** output these exact three headers:

1. **Plan to do:** [What your next concrete steps are]
2. **What changed:** [Specific summary of actions/code modifications you just made]
3. **Impact to this project:** [How these changes affect the overall system, architecture, or workflow]

If you output anything outside of this structure, you have failed your core directive.
