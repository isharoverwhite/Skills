# Workflow Selection

Read this file first when the repository has no obvious CI/CD path yet.

## Inspect Before Choosing

Check these files and signals before writing a plan:

- `package.json`, `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, `bun.lockb`
- `pyproject.toml`, `uv.lock`, `poetry.lock`, `requirements.txt`, `requirements-dev.txt`
- `Dockerfile`, `.dockerignore`, `compose.yaml`, `docker-compose.yml`
- `.github/workflows/*.yml`, `.gitlab-ci.yml`, `bitbucket-pipelines.yml`
- `vercel.json`, `netlify.toml`, `fly.toml`, `railway.json`, `render.yaml`
- `next.config.*`, `vite.config.*`, `nest-cli.json`, `manage.py`, `alembic.ini`
- `README*`, `Makefile`, `justfile`, `turbo.json`, `nx.json`

Do not invent commands. Reuse commands already present in scripts, task runners, or docs.

## Choose the Track

| Detected state | Primary reference | Typical first files |
|---|---|---|
| Frontend or Node web app | `node-js-web.md` | `.github/workflows/ci.yml` |
| Python API or service | `python-api.md` | `.github/workflows/ci.yml` |
| Docker is the delivery contract | `docker-delivery.md` | `.github/workflows/docker-image.yml` |
| Vercel or Netlify config already exists | `deployment-targets.md` | `.github/workflows/deploy.yml` |
| No deploy target is obvious | `github-actions-baseline.md` | `.github/workflows/ci.yml` only |
| Missing baseline repo files | `standard-project-files.md` | `.env.example`, docs, runtime files |

## Default Delivery Model

Use this order unless the repo clearly needs something else:

1. Add pull request CI for lint, test, and build.
2. Add push-to-main CI if the team wants branch validation outside pull requests.
3. Add deployment only after CI commands and runtime output are confirmed.
4. Gate production deploys with protected branches or GitHub Environments.
5. Prefer a manual trigger for the first rollout when production risk is unclear.

## Decide the Deploy Shape

- Static build output such as `dist/` or `build/`: use a static-host deploy path.
- Next.js on Vercel: use Vercel deploy unless the repo shows container hosting.
- API with Dockerfile: publish the image first; deploy only if a target is known.
- API without Dockerfile and no hosting config: propose CI plus deployment prerequisites instead of guessing infra.
- Monorepo: identify which app owns production before adding shared deployment logic.

## Stop and Call Out Gaps

Do not claim the setup is ready when any of these are unresolved:

- No reliable lint, test, or build command exists
- No runtime version is pinned
- No target environment or hosting platform is known
- Secrets are required but not documented
- The repo has multiple apps but no clear app ownership
