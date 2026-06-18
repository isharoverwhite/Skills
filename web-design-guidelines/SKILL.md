---
name: web-design-guidelines
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.

## 📝 CRITICAL Output Protocol (MANDATORY)

When you report back to the user, you **ABSOLUTELY MUST** use the following 3-point format and NOTHING ELSE. 
**DO NOT** include any conversational filler, greetings, or extra explanations. **ONLY** output these exact three headers:

1. **Plan to do:** [Your next concrete steps]
2. **What changed:** [Specific summary of actions/code modifications made]
3. **Impact to this project:** [How this affects the overall system, architecture, or workflow]

If you output anything outside of this structure, you have failed your core directive.
