---
name: fetch-library-docs
description: Fetches official documentation for external libraries and frameworks (React, Next.js, Prisma, FastAPI, Express, Tailwind, MongoDB, etc.) with 60-90% token savings via content-type filtering. Use this skill when implementing features using library APIs, debugging library-specific errors, troubleshooting configuration issues, installing or setting up frameworks, integrating third-party packages, upgrading between library versions, or looking up correct API patterns and best practices. Triggers automatically during coding work - fetch docs before writing library code to get correct patterns, not after guessing wrong.
---

# Library Documentation Skill

Fetches official library documentation with 60-90% token savings.

---

## WHEN TO INVOKE (Auto-Detection)

**INVOKE AUTOMATICALLY when:**

| Context | Detection Signal | Content Type |
|---------|------------------|--------------|
| **Implementing** | About to write code using library API | `examples,api-ref` |
| **Debugging** | Error contains library name (e.g., `PrismaClientError`) | `troubleshooting` |
| **Installing** | Adding new package, `npm install`, setup task | `setup` |
| **Integrating** | Connecting libraries ("use X with Y") | `examples,setup` |
| **Upgrading** | Version migration, breaking changes | `migration` |
| **Uncertain** | First use of library feature, unsure of pattern | `examples` |

**DO NOT INVOKE when:**
- Already have sufficient knowledge from training
- User pasted docs or has them open
- Task is about local/private code (use codebase search)
- Comparing libraries (use web search)

---

## DECISION LOGIC

### 1. Identify Library

```
Priority: User mention → Error message → File imports → package.json → Ask user
```

Examples:
- `PrismaClientKnownRequestError` → library = "prisma"
- `import { useState } from 'react'` → library = "react"
- `from fastapi import FastAPI` → library = "fastapi"

### 2. Identify Topic

```
Priority: User specifies → Error message → Feature being implemented → "getting started"
```

### 3. Select Content Type

| Task | Content Type |
|------|--------------|
| Implementing code | `examples,api-ref` |
| Debugging error | `troubleshooting,examples` |
| Installing/setup | `setup` |
| Integrating libs | `examples,setup` |
| Upgrading version | `migration` |
| Understanding why | `concepts` |
| Best practices | `patterns` |

---

## EXECUTION

**IMPORTANT: Always use the Python entry point (`fetch-docs.py`) for cross-platform compatibility.**

Use `python3` on Linux/macOS/WSL, `python` on Windows:

```bash
# With known library ID (faster - saves 1 API call)
python3 scripts/fetch-docs.py --library-id <id> --topic "<topic>" --content-type <types>

# With library name (auto-resolves)
python3 scripts/fetch-docs.py --library <name> --topic "<topic>" --content-type <types>
```

> **Windows note:** Use `python` instead of `python3` (e.g., `python scripts/fetch-docs.py ...`)

### Quick Library IDs

| Library | ID |
|---------|----|
| React | `/reactjs/react.dev` |
| Next.js | `/vercel/next.js` |
| Prisma | `/prisma/docs` |
| Tailwind | `/tailwindlabs/tailwindcss.com` |
| FastAPI | `/tiangolo/fastapi` |

See [references/library-ids.md](references/library-ids.md) for complete list.

---

## ERROR HANDLING (Quick Reference)

| Error | Action |
|-------|--------|
| `[LIBRARY_NOT_FOUND]` | Try spelling variations |
| `[LIBRARY_MISMATCH]` | Use --library-id directly |
| `[EMPTY_RESULTS]` | Broaden topic or use `--content-type all` |
| `[RATE_LIMIT_ERROR]` | Check API key setup |

**Call Budget**: Context7 allows 3 calls/question. Use `--library-id` to save 1 call.

See [references/context7-tools.md](references/context7-tools.md) for full error handling.

---

## REFERENCES

- [Library IDs](references/library-ids.md) - Complete library ID list
- [Usage Patterns](references/patterns.md) - Real-world examples
- [Context7 Tools](references/context7-tools.md) - API details, error codes, setup

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
