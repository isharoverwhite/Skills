# Docker Delivery

Use this file when the repository already has a `Dockerfile` or when container release is the safest neutral deployment target.

## File Checklist

Prefer these files in a container-based repository:

- `Dockerfile`
- `.dockerignore`
- `compose.yaml` if local dependency orchestration is required
- A documented healthcheck endpoint or process probe

## Build Rules

Apply these defaults unless the repo shows a different standard:

- Prefer multi-stage builds
- Use a non-root runtime user when practical
- Pin the base image to a major or minor version instead of floating tags
- Keep build context small through `.dockerignore`
- Inject secrets at deploy time, not during image build unless the platform requires build-time secrets

## Tagging Rules

Use immutable image identifiers:

- Commit SHA for traceability
- Semver tag when releases are tagged
- `latest` only on the main release branch if the team actually uses it

## Registry Guidance

- Use GHCR when GitHub is the center of gravity and no other registry is required
- Use cloud-native registry only when the deployment target needs it
- Prefer OIDC or workload identity where possible

## GitHub Actions Path

The standard file is:

- `.github/workflows/docker-image.yml`

Use `assets/github-actions/docker-image.yml` as the starting point.

## Deployment Guardrails

Do not claim Docker release is complete unless:

- The image builds successfully
- The exposed port and startup command match the app
- The runtime environment variables are documented
- The downstream deployment target is known or explicitly left as a follow-up step
