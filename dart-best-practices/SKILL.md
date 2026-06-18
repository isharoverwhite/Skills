---
name: dart-best-practices
description: |-
  General best practices for Dart development.
  Covers code style, effective Dart, and language features.
license: Apache-2.0
---

# Dart Best Practices

## 1. When to use this skill
Use this skill when:
-   Writing or reviewing Dart code.
-   Looking for guidance on idiomatic Dart usage.

## 2. Best Practices

### Multi-line Strings
Prefer using multi-line strings (`'''`) over concatenating strings with `+` and
`\n`, especially for large blocks of text like SQL queries, HTML, or
PEM-encoded keys. This improves readability and avoids
`lines_longer_than_80_chars` lint errors by allowing natural line breaks.

**Avoid:**
```dart
final pem = '-----BEGIN RSA PRIVATE KEY-----\n' +
    base64Encode(fullBytes) +
    '\n-----END RSA PRIVATE KEY-----';
```

**Prefer:**
```dart
final pem = '''
-----BEGIN RSA PRIVATE KEY-----
${base64Encode(fullBytes)}
-----END RSA PRIVATE KEY-----''';
```

### Line Length
Avoid lines longer than 80 characters, even in Markdown files and comments.
This ensures code is readable in split-screen views and on smaller screens
without horizontal scrolling.

**Prefer:**
Target 80 characters for wrapping text. Exceptions are allowed for long URLs
or identifiers that cannot be broken.

## Discovery

### Multi-line Strings
To find candidates for multi-line strings, search for string concatenation
with `+` involving newlines:
- **Regex**: `['"]\s*\+\s*['"]`
- **Regex**: `\+\s*['"].*\\n`

### Line Length
- Rely on the `lines_longer_than_80_chars` lint from the analyzer.

## Related Skills

- **[dart-modern-features]**: For idiomatic
  usage of modern Dart features like Pattern Matching (useful for deep JSON
  extraction), Records, and Switch Expressions.

[dart-modern-features]: https://github.com/kevmoo/dash_skills/blob/main/.agent/skills/dart-modern-features/SKILL.md

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
