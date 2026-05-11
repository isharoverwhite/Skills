# Portfolio Git Workflow Baseline

Use this reference when the user asks to follow the Portfolio repository guide exactly, or when the target repo exposes the same npm script structure.

## Validation Ladder

Map the change scope to the smallest command set that still proves safety:

- Small docs or text-only changes:
  ```bash
  npm run lint
  ```
- Code or logic changes:
  ```bash
  npm run lint && npm run typecheck && npm run test:unit
  ```
- Merge or release preparation:
  ```bash
  npm run ci:essential
  ```

Never commit or push when the working tree includes out-of-scope files, secrets, or generated junk.

## Commit Message Standard

Use bracket-tag commits:

```text
[tag] <short summary>
```

Common types:
- `[feat]`
- `[fix]`
- `[docs]`
- `[chore]`
- `[ci]`
- `[refactor]`

Examples:
- `[feat] add Articles section to homepage`
- `[fix] support private project recent activity`
- `[docs] update AGENTS.md`
- `[chore] update next.js version`
- `[ci] slim down default Jenkins verification path`
- `[refactor] extract ChatWidget into smaller components`

Keep each commit atomic. Do not mix a new feature, an unrelated fix, and cleanup in one commit.

## Push Readiness

Confirm all of these before recommending `git push`:

1. The current branch matches the task target.
2. Local state is in sync with upstream, or the user explicitly accepts the divergence.
3. The minimum required validation has run.
4. No junk files are included, especially:
- local database files
- generated build artifacts
- temporary dist folders
- secrets or machine-specific files

## Tag And Release

When the repo uses `package.json` versioning, prefer `npm version`:

- Patch:
  ```bash
  npm version patch -m "[chore] bump version to %s"
  ```
- Minor:
  ```bash
  npm version minor -m "[chore] bump version to %s"
  ```
- Major:
  ```bash
  npm version major -m "[chore] bump version to %s"
  ```

If manual tagging is needed, use an annotated tag:

```bash
git tag -a v2.0.1 -m "Release v2.0.1: Fix Docker icon and UI glitches"
```

Push order:

```bash
git push origin main
git push origin v2.0.1
git push origin --tags
```

If the branch and tag should move together, prefer:

```bash
git push origin main --follow-tags
```

## Release Checklist

1. Confirm `git status` is clean for the intended scope.
2. Run `npm run ci:essential`.
3. Bump version with `npm version`.
4. Push branch and tags.
5. Run any final packaging or image build that the repo expects.
