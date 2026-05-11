# Standard Project Files

Use this file when the repository needs a baseline file checklist before CI/CD can be considered standard.

## Core Files

These files should usually exist in a healthy application repository:

- `README.md`: local setup, test, build, deploy notes, required environment variables
- `.gitignore`: excludes build output, local environment files, editor caches
- `.env.example`: documents non-secret runtime variables without exposing values
- `LICENSE`: optional but common for public or shared internal repos
- `docs/deployment.md` or equivalent: useful when deployment requires manual prerequisites

## GitHub-Oriented Files

These files are common when GitHub Actions is the CI/CD platform:

- `.github/workflows/ci.yml`: lint, test, build
- `.github/workflows/deploy.yml`: deployment or release workflow
- `.github/CODEOWNERS`: optional but useful for approval routing
- `.github/dependabot.yml`: optional dependency update automation
- `.github/pull_request_template.md`: optional review checklist

## Node.js and TypeScript Files

Look for or recommend these when the repo is JavaScript or TypeScript based:

- `package.json`
- Exactly one lockfile: `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, or `bun.lockb`
- `.nvmrc` or `packageManager` and `engines` in `package.json`
- `tsconfig.json` when TypeScript is used
- Lint and format config such as `eslint.config.js` or `.eslintrc.*`
- Test config such as `vitest.config.*`, `jest.config.*`, or framework defaults

## Python Files

Look for or recommend these when the repo is Python based:

- `pyproject.toml`
- A lockfile or dependency source such as `uv.lock`, `poetry.lock`, or `requirements.txt`
- `.python-version` or an explicit version in CI
- Test config in `pyproject.toml`, `pytest.ini`, or `tox.ini`
- Ruff, mypy, or formatter config when those tools are part of the standard

## Container Files

Treat these as standard when the app is delivered as a container:

- `Dockerfile`
- `.dockerignore`
- `compose.yaml` or `docker-compose.yml` for local dependencies when needed
- A documented healthcheck endpoint or command

## Deployment Target Files

These files usually signal the preferred CD path:

- `vercel.json`
- `netlify.toml`
- `fly.toml`
- `railway.json`
- `render.yaml`
- Terraform, Helm, or cloud service descriptors if the team owns infrastructure directly

## Minimum Documentation After Setup

After adding CI/CD, update at least one user-facing document with:

- Required secrets and where they live
- Branches or tags that trigger deployment
- Expected build artifacts or container images
- Rollback notes if deployment is automated
