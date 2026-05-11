# Node.js, Next.js, Vite, and NestJS

Use this file when the repository is based on JavaScript or TypeScript.

## Detect the Stack

Look for these signals:

- `package.json` always
- `next.config.*` for Next.js
- `vite.config.*` for Vite
- `nest-cli.json` for NestJS
- `turbo.json`, `nx.json`, or workspace fields for monorepos

## Standard Scripts

Prefer repositories that expose these scripts in `package.json`:

- `lint`
- `test`
- `build`
- `typecheck` when TypeScript is used
- `start` or framework equivalent for runtime documentation

If a script is missing, call out the gap instead of pretending it exists.

## Package Manager Rules

| Signal | Install command | Cache strategy |
|---|---|---|
| `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` | `actions/setup-node` with `cache: pnpm` |
| `package-lock.json` | `npm ci` | `actions/setup-node` with `cache: npm` |
| `yarn.lock` | `yarn install --frozen-lockfile` or repo standard | `actions/setup-node` with `cache: yarn` |
| `bun.lockb` or `bun.lock` | use Bun setup and repo standard install | use Bun-specific cache only if the repo already relies on it |

## CI Order

Use this order for the default Node.js workflow:

1. Install dependencies
2. Run lint
3. Run tests
4. Run typecheck if present
5. Run build

## Framework Notes

### Next.js

- If Vercel is already the platform, read `deployment-targets.md` and prefer Vercel deployment.
- If self-hosted, confirm whether the repo expects standalone output, Node runtime, or container deployment.
- Do not assume `.next/` is directly deployable without the matching runtime strategy.

### Vite or SPA Frontend

- Expect build output in `dist/`
- Prefer static-host deployment
- Confirm SPA routing behavior if the target host needs rewrite rules

### NestJS or Node API

- Expect compiled output in `dist/`
- Run unit tests and e2e tests only if the scripts exist
- Prefer Docker release when no app platform is specified

## Common File Gaps

Recommend or verify these files when they are missing:

- `.nvmrc` or runtime pinning in `package.json`
- `.env.example`
- Workspace config for monorepos
- A lint and test config appropriate to the stack

## Template

Start from `assets/github-actions/node-ci.yml` for the default CI path.
