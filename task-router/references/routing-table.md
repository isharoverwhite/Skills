# IT Department Task Routing Reference

> 🚨 **CRITICAL**: This directory is your official routing table. You must use it to cross-reference tasks with the appropriate IT Role, Sub-Agent Reference, and Bash Flag (`pro` or `flash`). You MUST route tasks via the bash command `claude-ds [pro|flash] --print "..."`.

## 🏢 IT Department Directory

| IT Role | Sub-Agent Reference | Bash Flag | Cost Profile | Description |
|---------|---------------------|-----------|--------------|-------------|
| **Developer** | `coder` | `pro` | 🔴 High | Code generation, complex refactoring, API building. |
| **QA / Tester** | `tester` | `pro` | 🔴 High | Designing robust test suites, deep debugging, regression. |
| **Architect** | `planner` | `pro` | 🔴 High | System design, schema design, architecture, tech stack selection. |
| **Doc-Writer** | `doc-author` | `flash` | 🟢 Low | Documentation, READMEs, changelogs, user manuals. |
| **Project Manager** | `product-manager` | `flash` | 🟢 Low | Scoping, requirements gathering, PRDs, user stories. |
| **DevOps / SysAdmin** | `project-analysis` | `flash` | 🟢 Low | Codebase scanning, tech stack analysis, structure mapping. |

## 🔑 Keyword-to-Role Mapping

### Developer (`coder` / `pro`)
implement, write code, build, create widget, add feature, fix bug, refactor, develop, code, function, class, method, API endpoint, route, screen, page, component, controller, provider, bloc, cubit, service, repository, model, DTO, helper, utility, migration, script, command

### QA / Tester (`tester` / `pro`)
test, unit test, widget test, integration test, coverage, mock, mockito, mocktail, assert, verify, expect, debug, bug fix, test failure, flaky, MissingPluginException, pumpAndSettle, finder, test doubles, fake, stub, spy, test coverage, regression

### Doc-Writer (`doc-author` / `flash`)
document, docs, readme, PDF, DOCX, write doc, guide, manual, specification, report, export, print, changelog, release notes, API docs, user manual, setup guide, contributing, license, README, markdown, documentation site

### Architect (`planner` / `pro`)
plan, architecture, design doc, schema, roadmap, sprint, timeline, milestone, structure, tech design, proposal, breakdown, epic, story points, estimation, dependency graph, system design, data flow, ERD, UML, sequence diagram, migration plan, rollback plan

### Project Manager (`product-manager` / `flash`)
requirement, user story, feature request, PRD, scope, priorities, backlog, stakeholder, roadmap, product spec, acceptance criteria, MVP, OKR, KPI, business value, user research, A/B test, launch plan, go-to-market, competitive analysis

### DevOps / SysAdmin (`project-analysis` / `flash`)
analyze project, tech stack, coding style, language, dependencies, framework, structure, patterns, what is this project, code base overview

## 🔀 Multi-Category Workflow (Sequencing)

> 🚨 **CRITICAL**: For tasks spanning multiple IT domains, you MUST chain them sequentially using bash commands. Do not spawn them in parallel if they depend on each other.

| Task Pattern | Step 1 | Step 2 | Step 3 |
|-------------|---------|---------|---------|
| Build feature + write tests | `pro` → `coder` | `pro` → `tester` | — |
| Plan feature + write PRD | `flash` → `product-manager` | `pro` → `planner` | — |
| Design architecture + document | `pro` → `planner` | `flash` → `doc-author` | — |
| Requirements → planning → coding | `flash` → `product-manager` | `pro` → `planner` | `pro` → `coder` |
| Build + test + document | `pro` → `coder` | `pro` → `tester` | `flash` → `doc-author` |
