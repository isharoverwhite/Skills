---
name: github-commit-workflow
description: Review and execute GitHub commit, push, and tag workflows with repo inspection, validation gates, commit message drafting, dirty-tree checks, upstream assessment, and release tagging. Use when Codex needs to prepare or review a commit, decide whether a branch is ready to push, choose a bracket-tag commit message like `[feat] ...`, or guide a GitHub release safely in a Git repository.
---

# GitHub Commit Workflow

Use this skill to make commit and push decisions from actual repo state instead of assumptions.

Read the repository before touching Git. If `AGENTS.md` exists, read it first. If the directory is not a Git repository, say so clearly and switch to static analysis.

## Core Workflow

1. Inspect repo context before proposing Git actions.
- Read `AGENTS.md`, `README`, product docs, manifest files, and CI config when they exist.
- Identify the repo-native validation commands instead of assuming generic commands.
- Note the module or directory that the user actually wants to change.

2. Collect Git evidence.
- Run `git status --short --branch`
- Run `git branch --show-current`
- Run `git remote -v`
- Run `git log --oneline --decorate -n 10`
- Run `git diff --stat` and `git diff --cached --stat`
- Run `git rev-list --left-right --count @{upstream}...HEAD` when an upstream exists

3. Stop on unsafe conditions.
- Dirty files outside the task scope
- Secrets, local databases, generated outputs, or artifacts that should not be versioned
- Missing upstream or wrong target branch for the stated goal
- Ambiguous commit scope because staged and unstaged work are mixed

4. Choose the smallest valid validation set.
- Docs-only or small text changes: run the lightest repo-native lint or docs validation command
- Logic, config, or schema changes: run lint, typecheck, and the relevant automated tests
- Merge or release preparation: run the broadest CI-equivalent command the repo already defines
- If the user asks for the Portfolio workflow or the repo exposes matching npm scripts, read `references/portfolio-guide-baseline.vi.md`

5. Prepare the commit.
- Stage only files inside the intended scope
- Confirm the commit solves one objective only
- Draft a bracket-tag commit message that matches the diff
- Call out missing tests, docs, migrations, or screenshots before committing
- If the user asked only for review, do not commit

6. Assess push and tag readiness separately.
- Confirm the remote, branch, and upstream target
- Confirm the local branch is not behind upstream unless the user explicitly accepts that risk
- Confirm validation appropriate to the change has run
- Before push, tell the user which branch, remote, and commit(s) will move
- Before tag or release, confirm the repo's version source and tag format

## Commit Message Rules

Use the repository's bracket-tag format by default.

Format:
```text
[tag] <short summary>
```

Use these types by default:
- `[feat]`
- `[fix]`
- `[docs]`
- `[chore]`
- `[ci]`
- `[refactor]`
- `[test]`

Rewrite or reject the message when:
- One commit mixes multiple objectives
- The summary does not match the diff
- The text is vague, such as `update files` or `misc changes`
- Feature work and unrelated cleanup are bundled together

## Push And Tag Rules

Do not recommend `git push` until all of these are true:
- The working tree is clean for the intended scope
- The staged or committed changes reflect the task exactly
- The minimum safe validation has run
- The correct branch and upstream are selected
- Obvious secrets, artifacts, and junk files are excluded

Do not push automatically unless the user explicitly asks for it.

When the user asks for a tag or release:
- Prefer the repo's existing version source and tag pattern
- If the repo uses `npm version`, prefer that over hand-editing version strings
- If tagging manually, use annotated tags
- Announce the exact branch, remote, version, and tag before push

## Standard Output

Return results in this shape unless the user asks for something else:

### Project Summary
- Repo purpose and relevant module
- Git-relevant docs or config found

### Findings
- Scope risks
- Validation gaps
- Files that should not be committed

### Git Assessment
- Current branch and upstream state
- Commit quality or proposed commit message
- Push readiness and blockers

### Next Action
- Smallest safe next step
- Exact commands to run when the user wants execution

## Reference File

Read `references/portfolio-guide-baseline.vi.md` when:
- The user wants the exact workflow derived from the Portfolio repository
- The repo uses matching npm scripts such as `lint`, `typecheck`, `test:unit`, or `ci:essential`
- Release tagging or version bump flow needs a concrete Node/npm baseline

## Example Requests

- "Review this repo and tell me if my branch is ready to commit."
- "Draft a bracket-tag commit message for these staged changes."
- "Check whether it is safe to push this branch."
- "Prepare a release tag and tell me the exact commands."
- "Follow my GitHub commit guide and help me commit this repo."

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
