# GitHub Actions Baseline

Use this file when GitHub Actions is the chosen or default platform.

## Default Structure

Prefer two workflow files instead of one oversized file:

- `.github/workflows/ci.yml`
- `.github/workflows/deploy.yml`

Keep CI and CD separate unless the repository is trivial and deployment is low-risk.

## Standard CI Conventions

Use these conventions by default:

- Trigger on `pull_request`
- Trigger on `push` to the main integration branch if the team uses it
- Use least-privilege `permissions`
- Use `concurrency` to cancel stale runs on the same branch
- Cache dependencies only through the package manager integration for the detected stack

## Standard CI Shape

Structure the workflow in this order:

1. Checkout code
2. Set up runtime
3. Restore dependency cache
4. Install dependencies
5. Run lint
6. Run tests
7. Run build

Skip steps only when the repository truly does not support them.

## Standard CD Conventions

Use these defaults unless the repo already proves another policy:

- Deploy on `push` to the protected production branch
- Add `workflow_dispatch` for manual re-runs and first-time rollout
- Use GitHub Environments for staging and production
- Require explicit secrets only in the deploy workflow
- Publish artifacts or images with immutable identifiers such as commit SHA

## Minimal Snippets

Use patterns like these, then adapt them to the stack:

```yaml
permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

```yaml
on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:
```

## Workflow File Checklist

Before calling a GitHub Actions setup complete, confirm:

- The workflow refers to commands that exist
- The cache matches the actual package manager
- The branch names match the real branching model
- The runtime version is pinned by file or CI config
- The deploy workflow uses environment protection where risk is non-trivial

## Template Files

Start from these templates when they fit the repo:

- `assets/github-actions/node-ci.yml`
- `assets/github-actions/python-ci.yml`
- `assets/github-actions/docker-image.yml`
- `assets/github-actions/deploy-vercel.yml`
