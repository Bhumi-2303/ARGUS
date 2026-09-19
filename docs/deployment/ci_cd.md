# ARGUS CI/CD Pipeline

The ARGUS CI/CD pipeline guarantees system stability and code quality on every PR and push to `main` and `develop` branches.

## CI Workflow

The workflow is defined in `.github/workflows/ci.yml` and consists of 4 strictly separated stages that must all pass.

### Stage 1: Linting & Type Checking
- Validates python versions and requirements.
- Uses `ruff` for fast linting and formatting.
- Uses `mypy` for static type checking across the backend schemas and services.

### Stage 2: Unit & Integration Tests (Backend)
- Uses `pytest` to execute Level 1 (Unit), Level 2 (Integration), and Level 3 (End-to-End) tests.
- Uses deterministic, non-sensitive fixtures representing different edge cases (e.g. `policy_failure`, `llm_unavailable`).
- Does **not** execute ML training steps.

### Stage 3: Frontend Build
- Runs `npm install` and `npm run build` using Node.js to ensure the React UI compiles cleanly.
- Catches strict TypeScript errors in the frontend build pipeline.

### Stage 4: Docker Configuration & Smoke Test
- Validates `docker-compose.yml` via `docker compose config -q`.
- Builds the `api/Dockerfile` to guarantee containerization configurations are unbroken.

## Release Workflow
- Merging to `main` with passing CI will ultimately trigger the creation of a release candidate image.
- A semantic version tag (e.g., `v1.2.0`) triggers a production push to the container registry.

## Failure Handling
The CI pipeline is designed to **fail fast and loudly** when:
- Backend schemas break, or Pydantic validation fails.
- Any backend unit, integration, or E2E test fails.
- The frontend build process emits structural TypeScript errors or fails to bundle.
- Dockerfiles or Compose files contain syntactic/structural errors.
