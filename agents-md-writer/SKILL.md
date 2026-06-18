---
name: agents-md-writer
description: Create or update AGENTS.md playbooks for repositories that use multiple collaborating agents. Use when Codex must define agent roles, phased delivery workflow (Requirement, Design, Implementation, Test), mandatory deliverables (PRD.md, design docs, PROJECT_STATUS.md), and communication logging rules in AGENT_COMMUNICATION.log.
---

# AGENTS.md Writer

## Overview
Create structured `AGENTS.md` files for multi-agent software projects. Keep the document deterministic: explicit phases, clear role boundaries, approval gates, and audit logging.

## Workflow
1. Read user requirements and collect project-specific constraints.
2. Read `references/claude-code-process-reference.vi.md` when the user does not provide a stronger reference.
3. Generate a base file from `references/agents-md-template.vi.md`.
4. Adapt terminology, agent names, and file paths to the repository.
5. Validate section completeness before returning results.

## Mandatory Sections
Include all sections below in the final `AGENTS.md`:
1. Process overview with phase order.
2. Detailed workflow for each phase.
3. Role and responsibility matrix for all agents.
4. User-approval checkpoints between phases.
5. Project tracking file format (`PROJECT_STATUS.md` or project-specific equivalent).
6. Inter-agent communication log format and rules.
7. Working principles and exception handling.
8. End-to-end example workflow.

## Adaptation Rules
1. Preserve phase order unless the user explicitly asks to change it.
2. Keep instructions actionable and imperative.
3. Use explicit file paths for all expected artifacts.
4. Keep log format strict: `[YYYY-MM-DD HH:MM:SS] SENDER -> RECEIVER | REQUEST_BRIEF`.
5. Keep `REQUEST_BRIEF` concise (target <= 100 characters).
6. Distinguish clearly between events that must be logged and events that should not be logged.
7. Add an explicit "deviation" section when the user requests a process exception.

## Scripted Generation
Use `scripts/render_agents_md.py` to render a base draft from template placeholders.

Example:
```bash
python3 scripts/render_agents_md.py \
  --project-name "FutureBoxes v2" \
  --main-agent "main" \
  --ba-agent "agent-ba" \
  --uiux-agent "agent-uiux" \
  --react-agent "agent-react" \
  --output AGENTS.md
```

## Resources
- `references/claude-code-process-reference.vi.md`: Baseline process and governance rules.
- `references/agents-md-template.vi.md`: Ready-to-render AGENTS.md template with placeholders.
- `scripts/render_agents_md.py`: Deterministic renderer for template placeholders.

## Validation Checklist
Run this checklist before final output:
1. Confirm no unresolved placeholders like `{{PROJECT_NAME}}` remain.
2. Confirm all phases include objective, workflow, and checkpoint.
3. Confirm agent names are consistent across all sections.
4. Confirm project status tracking format is present.
5. Confirm communication logging rules include required and excluded events.
6. Confirm example workflow matches the defined phase order.

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
