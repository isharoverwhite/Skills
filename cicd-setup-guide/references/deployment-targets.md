# Deployment Targets

Use this file after the stack is identified and the hosting target matters.

## Target Matrix

| Target | Use when | Common files | Typical CD shape |
|---|---|---|---|
| Vercel | Next.js or frontend app already linked to Vercel | `vercel.json`, project settings | Deploy with Vercel CLI or platform integration |
| Netlify | Static frontend or framework already on Netlify | `netlify.toml` | Build static site and deploy artifact |
| Fly.io | Containerized app or lightweight fullstack service | `fly.toml` | Build image and deploy with Fly CLI |
| Railway or Render | App already configured there or simple service hosting is preferred | `railway.json`, `render.yaml` | Provider CLI or API deploy after build |
| Cloud Run | Containerized service with GCP | Dockerfile, GCP config | Build image, push registry, deploy revision |
| ECS or App Runner | AWS-managed container hosting | task defs, IaC, Dockerfile | Build image, push registry, update service |

## Default Recommendations

- Next.js with clear Vercel ownership: prefer Vercel
- Static SPA: prefer Netlify, Vercel, or another static host already used by the repo
- API with Dockerfile and no strong provider signal: start with image build, then align deployment to the platform the team chooses
- Team-owned cloud infrastructure: follow the existing IaC instead of inventing direct CLI deployment

## Vercel Notes

- Required secrets are usually `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID`
- Preview deploys on pull requests are common
- Production deploy usually follows `push` to the protected branch
- Use `assets/github-actions/deploy-vercel.yml` as the default starting point

## Cloud Container Notes

For Cloud Run, ECS, App Runner, Fly.io, Railway, or Render:

- Ensure the image contract is stable first
- Prefer deploy jobs that consume an immutable image tag
- Document environment variables separately from the workflow file
- Keep platform-specific credentials out of the repo

## Unknown Target

If the target is still unknown, stop at CI plus image or artifact creation. That keeps the repository release-ready without guessing production infrastructure.
