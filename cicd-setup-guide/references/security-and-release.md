# Security and Release

Use this file before recommending production auto-deploy or marking the setup as release-ready.

## Secrets and Configuration

Apply these defaults:

- Never commit `.env` files with real values
- Add or update `.env.example`
- Store deployment credentials in GitHub Secrets or GitHub Environments
- Prefer OIDC, workload identity, or short-lived tokens over long-lived static cloud keys

## Environment Strategy

Use environment separation when risk is non-trivial:

- `staging` for pre-production validation
- `production` for protected releases

Attach reviewers or approval gates to the production environment when the platform supports it.

## Branch and Trigger Safety

Prefer these defaults:

- CI on pull requests
- Deployment only from protected branches, tags, or manual dispatch
- No production deploys from feature branches
- Concurrency protection for deploy workflows so stale runs do not overwrite newer releases

## Release Checklist

Before calling a repo ready for deployment, confirm:

- The app has a reproducible build
- The required secrets are documented
- The deploy workflow points to the correct artifact, image, or provider project
- The branch strategy matches the actual repository workflow
- A rollback path is at least described

## Rollback Guidance

Document one of these patterns:

- Re-deploy the previous artifact or image tag
- Roll back to the previous provider deployment
- Disable auto-deploy and use manual promotion until confidence improves

## User-Facing Deliverable

Include these items in the final answer when you use this skill:

- Files added or modified
- Secrets and environments required
- Trigger rules
- Validation steps
- Remaining risks or manual prerequisites
