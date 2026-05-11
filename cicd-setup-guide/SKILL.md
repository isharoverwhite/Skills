---
name: cicd-setup-guide
description: Set up, review, and explain modern CI/CD for common application repositories using GitHub Actions as the default path. Use when Codex needs to inspect a repo, choose a standard pipeline, add workflow files, document secrets and environments, or guide users through CI/CD setup for Node.js, Next.js, Vite, NestJS, Python, FastAPI, Django, Dockerized services, or popular deployment targets such as Vercel, Netlify, Fly.io, Railway, Cloud Run, or ECS.
---

# CI/CD Setup Guide

Use this skill to build the smallest safe CI/CD path that matches the repository instead of forcing a one-size-fits-all pipeline.

Default to GitHub Actions unless the repo already uses another CI/CD system. Extend existing automation when possible instead of replacing it.

## Core Workflow

1. Inspect the repository before proposing any workflow files.
Look for `package.json`, lockfiles, `pyproject.toml`, `requirements*.txt`, `Dockerfile`, existing `.github/workflows`, deploy configs such as `vercel.json` or `fly.toml`, and actual lint, test, and build commands.

2. Classify the repository before choosing a pipeline.
- Static frontend: Vite, React SPA, Angular, or another build-to-static app
- Fullstack JS app: Next.js, Remix, Nuxt, or another framework with server runtime
- API or worker: NestJS, Express, FastAPI, Django, Celery worker, cron service
- Container-first service: Dockerfile already defines the delivery contract
- Monorepo: multiple apps or packages that need scoped jobs instead of root-only assumptions

3. Read only the relevant references.
- Start with `references/workflow-selection.md`
- Read `references/standard-project-files.md` when the repo is missing baseline setup files
- Read `references/github-actions-baseline.md` for workflow structure and conventions
- Read `references/node-js-web.md` for Node.js, Next.js, Vite, or NestJS
- Read `references/python-api.md` for Python, FastAPI, or Django
- Read `references/docker-delivery.md` for image build and registry publishing
- Read `references/deployment-targets.md` when the hosting target matters
- Read `references/security-and-release.md` before recommending auto-deploy or handling secrets

4. Implement the minimum viable pipeline first.
- Add CI before CD if the repo has no automation
- Separate verification and deployment into different jobs or different workflow files
- Run only commands that actually exist in the repo
- Prefer `workflow_dispatch` plus protected branches until automatic deploys are clearly safe
- Reuse platform-native deployment when the repo already points to Vercel, Netlify, Fly.io, Railway, Cloud Run, or ECS

5. Document prerequisites as part of the deliverable.
- List required secrets and GitHub Environments
- State which branches trigger CI and CD
- State what artifact or image gets produced
- State what rollback or manual recovery path exists
- Call out unresolved risks and assumptions explicitly

6. Validate the proposal before calling it complete.
- Check that the repo has matching scripts or commands
- Check that caches align with the actual package manager
- Check that the deploy job uses the correct build output or image tag
- Check that secrets are not committed and `.env.example` exists when runtime configuration is needed
- Keep the first release path reviewable and reversible

## Decision Rules

- If a repo already has `.github/workflows/*.yml`, extend them instead of rewriting from scratch.
- If the deployment target is unclear, stop at CI plus image build or artifact creation rather than inventing production deployment.
- If the app is Next.js and the repo already uses Vercel, prefer Vercel deployment instead of self-hosting unless the repo shows a different runtime.
- If the app builds static assets, prefer a static-host workflow rather than a server deployment.
- If the app is an API and no platform is defined, prefer a Docker release path because it keeps hosting decisions open.
- If the repo is a monorepo, scope jobs to the relevant workspace and avoid assuming root-level scripts cover every app.
- If secrets or cloud credentials would be needed, prefer OIDC or short-lived credentials over long-lived static keys.

## Standard Output

Return results in this shape unless the user asks for something else:

### Project Summary
- Repo type and detected stack
- Existing CI/CD state
- Most likely deployment model

### Findings
- Gaps in scripts, files, or release readiness
- Risks around secrets, missing tests, or ambiguous hosting
- Smallest safe next step

### CI/CD Plan
- Files to add or modify
- Trigger strategy
- Build, test, and deploy commands
- Required secrets and environments

### Validation
- Local checks to run
- GitHub-side checks to confirm
- Remaining unknowns or manual steps

## Reference Files

Read these files selectively instead of loading everything:

- `references/workflow-selection.md`: detect the stack, delivery model, and safest starting point
- `references/standard-project-files.md`: check which project files should exist before or alongside CI/CD
- `references/github-actions-baseline.md`: apply default GitHub Actions patterns
- `references/node-js-web.md`: configure JavaScript or TypeScript apps
- `references/python-api.md`: configure Python services and APIs
- `references/docker-delivery.md`: build, tag, and publish Docker images
- `references/deployment-targets.md`: match the workflow to Vercel, Netlify, Fly.io, Railway, Cloud Run, or ECS
- `references/security-and-release.md`: handle secrets, environments, approvals, and release safety

## Asset Templates

Start from these templates when the repo is close to the default case, then adapt them:

- `assets/github-actions/node-ci.yml`
- `assets/github-actions/python-ci.yml`
- `assets/github-actions/docker-image.yml`
- `assets/github-actions/deploy-vercel.yml`

## Resources

### references/

Load only the references needed for the detected stack and deployment target. Do not dump every reference into context.

### assets/

Treat the templates as starting points, not drop-in truth. Align them to the repo's package manager, runtime version, hosting provider, and branch strategy before using them.

## Example Requests

- "Set up CI/CD for my Next.js app on Vercel."
- "Add GitHub Actions for a FastAPI API that deploys as a Docker container."
- "Review this repo and tell me what files are missing for a standard CI/CD setup."
- "Create a baseline CI workflow for a pnpm monorepo without changing the deploy path yet."
