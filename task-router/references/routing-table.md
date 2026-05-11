# Task Routing Reference

> 🚨 **QUAN TRỌNG**: Bảng này chỉ dùng để tra cứu agent+model trước khi chạy Bash. Mọi routing PHẢI thông qua lệnh `claude-ds [pro|flash] --print "..."`. Không được phép chỉ output text.

## Agent → Model Mapping

| Agent | Model | Bash Flag | Cost Profile |
|-------|-------|-----------|--------------|
| `coder` | `deepseek-v4-pro` | `pro` | 🔴 Code generation needs deep reasoning |
| `tester` | `deepseek-v4-pro` | `pro` | 🔴 Test design needs high reasoning |
| `planner` | `deepseek-v4-pro` | `pro` | 🔴 Architecture decisions impact entire system |
| `doc-author` | `deepseek-v4-flash` | `flash` | 🟢 Text generation, lightweight |
| `product-manager` | `deepseek-v4-flash` | `flash` | 🟢 Business writing, requirements |
| `project-analysis` | `deepseek-v4-flash` | `flash` | 🟢 Static code reading, pattern matching |

## Keyword-to-Agent Mapping

### coder → `claude-ds pro`
implement, write code, build, create widget, add feature, fix bug, refactor, develop, code, function, class, method, API endpoint, route, screen, page, component, controller, provider, bloc, cubit, service, repository, model, DTO, helper, utility, migration, script, command

### tester → `claude-ds pro`
test, unit test, widget test, integration test, coverage, mock, mockito, mocktail, assert, verify, expect, debug, bug fix, test failure, flaky, MissingPluginException, pumpAndSettle, finder, test doubles, fake, stub, spy, test coverage, regression

### doc-author → `claude-ds flash`
document, docs, readme, PDF, DOCX, write doc, guide, manual, specification, report, export, print, changelog, release notes, API docs, user manual, setup guide, contributing, license, README, markdown, documentation site

### planner → `claude-ds pro`
plan, architecture, design doc, schema, roadmap, sprint, timeline, milestone, structure, tech design, proposal, breakdown, epic, story points, estimation, dependency graph, system design, data flow, ERD, UML, sequence diagram, migration plan, rollback plan

### product-manager → `claude-ds flash`
requirement, user story, feature request, PRD, scope, priorities, backlog, stakeholder, roadmap, product spec, acceptance criteria, MVP, OKR, KPI, business value, user research, A/B test, launch plan, go-to-market, competitive analysis

### project-analysis → `claude-ds flash`
analyze project, tech stack, coding style, language, dependencies, framework, structure, patterns, what is this project, code base overview

## Multi-Category Tasks

> 🚨 Với task đa lĩnh vực: chạy Bash đến agent CHÍNH trước, rồi báo user về agent phụ. Không được liệt kê suông.

| Task Pattern | Bash #1 | Bash #2 | Bash #3 |
|-------------|---------|---------|---------|
| Build feature + write tests | `claude-ds pro` → `coder` | `claude-ds pro` → `tester` | — |
| Plan feature + write PRD | `claude-ds flash` → `product-manager` | `claude-ds pro` → `planner` | — |
| Design architecture + document | `claude-ds pro` → `planner` | `claude-ds flash` → `doc-author` | — |
| Requirements → planning → coding | `claude-ds flash` → `product-manager` | `claude-ds pro` → `planner` | `claude-ds pro` → `coder` |
| Build + test + document | `claude-ds pro` → `coder` | `claude-ds pro` → `tester` | `claude-ds flash` → `doc-author` |
