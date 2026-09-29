# ARGUS Production Deployment Guide

This guide details the operational standards and procedures for deploying the **ARGUS (Autonomous Risk-aware Grid Understanding & Security)** platform into production and mission-critical OT environments.

---

## 1. Production Architecture & Ingress

ARGUS operates as an air-gappable, hardened microservice designed to run behind a corporate or substation edge reverse proxy (e.g., NGINX, Envoy, Traefik, AWS ALB) that provides:

1. **TLS 1.3 Termination**: In-transit encryption must terminate at the ingress proxy or API gateway.
2. **Strict Host Routing**: Route requests for the ARGUS platform exclusively to port `8000`.
3. **HTTP Security Headers**: While ARGUS injects CSP, HSTS, and frame protections internally, ingress proxies should forward client IPs via `X-Forwarded-For` and `X-Real-IP`.

```
 Internet / Control Network
            │
            ▼
┌─────────────────────────┐
│ Ingress / Reverse Proxy │  (TLS 1.3, Rate-Limiting, DDoS Protection)
└───────────┬─────────────┘
            │ Internal Private Network
            ▼
┌─────────────────────────┐
│  argus-platform:latest  │  (Non-root, Cap-dropped, Read-only layout)
│  - FastAPI Engine       │
│  - ML Registry & SHAP   │
│  - Embedded Static UI   │
└─────────────────────────┘
```

---

## 2. Environment Configuration Reference

Production environments **fail-closed** at startup if required variables are missing or contain placeholder values.

| Variable | Required in Prod | Default (Dev) | Production Example | Description |
|---|---|---|---|---|
| `ENVIRONMENT` | **Yes** | `development` | `production` | Enables strict fail-closed security validations |
| `SECRET_KEY` | **Yes** | Placeholder | `64+ char random hex` | Cryptographic secret for signing session state |
| `OIDC_ENABLED` | **Yes** | `false` | `true` | Enforces JWT token validation on all endpoints |
| `OIDC_ISSUER` | **Yes** | None | `https://auth.grid-ops.internal` | Canonical issuer URI of enterprise IdP |
| `OIDC_AUDIENCE` | **Yes** | None | `argus-prod-api` | Expected `aud` claim in incoming JWTs |
| `OIDC_JWKS_URL` | **Yes** | None | `https://auth.grid-ops.internal/.well-known/jwks.json` | Remote JWKS endpoint (HTTPS mandatory) |
| `OIDC_ALGORITHMS` | No | `["RS256"]` | `["RS256", "ES256"]` | Asymmetric JWT signing algorithms |
| `CORS_ORIGINS` | **Yes** | `["*"]` | `["https://argus.grid-ops.internal"]` | Explicit origin allowlist (No wildcards/localhost) |
| `ARGUS_HOST` | No | `127.0.0.1` | `0.0.0.0` | Host interface binding for container |
| `ARGUS_PORT` | No | `8000` | `8000` | TCP port for API listener |
| `WORKERS` | No | `1` | `2` | Uvicorn worker process count |

---

## 3. Container Hardening Checklist

The production Docker container (`Dockerfile`) includes:

- **Multi-Stage Build**: Development toolchains (`gcc`, `g++`) are discarded after compilation; runtime contains only minimal C-runtime dependencies.
- **Non-Root Execution**: Runs as `argususer:argusgroup` (`UID=10001, GID=10001`).
- **Filesystem Permissions**: Code directories are marked read-only (`chmod 550`), eliminating runtime source tampering.
- **No-New-Privileges**: Set `security_opt: [ "no-new-privileges:true" ]` in Docker/Kubernetes.
- **Capability Dropping**: Drop all Linux capabilities: `cap_drop: [ "ALL" ]`.

---

## 4. Deployment Procedures

### A. Docker Compose Deployment

1. Prepare `.env.production` with authoritative credentials:
   ```bash
   chmod 600 .env.production
   ```
2. Verify Compose configuration:
   ```bash
   docker compose --env-file .env.production config -q
   ```
3. Launch container with resource constraints:
   ```bash
   docker compose --env-file .env.production up -d
   ```
4. Verify healthcheck status:
   ```bash
   docker compose ps
   ```

### B. Kubernetes Deployment (Pod Spec Excerpt)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: argus-platform
  namespace: security-monitoring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: argus-platform
  template:
    metadata:
      labels:
        app: argus-platform
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        fsGroup: 10001
      containers:
        - name: argus-api
          image: argus-platform:latest
          imagePullPolicy: IfNotPresent
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: false
            capabilities:
              drop:
                - ALL
          resources:
            limits:
              cpu: "2000m"
              memory: "2048Mi"
            requests:
              cpu: "500m"
              memory: "512Mi"
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /liveness
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /readiness
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
```

---

## 5. Health, Readiness, and Liveness Probes

ARGUS exposes three operational endpoints:

1. **`GET /health`**:
   - Status code: `200 OK`
   - Returns overall system status, model registry health, and active version.
2. **`GET /readiness`**:
   - Status code: `200 OK` (when models, data managers, and memory stores are initialized).
   - If any required model or artifact failed to verify integrity: returns `503 Service Unavailable`.
3. **`GET /liveness`**:
   - Status code: `200 OK`
   - Confirms HTTP event loop and server process responsiveness.

---

## 6. Secret Rotation & Runbook

### Key Rotation Procedure
1. Register new public key in the enterprise IdP JWKS endpoint with a unique `kid`.
2. ARGUS JWKS client automatically discovers the new key on cache miss (bounded at 1 refresh / 60 seconds).
3. Retire the old signing key from the IdP once all existing tokens expire.

### Disaster Recovery
1. Re-verify model and data hashes against `artifacts/manifest.json`:
   ```bash
   python scripts/verify_manifest.py
   ```
2. Run automated numerical test suite:
   ```bash
   python scripts/verify_ui_numbers.py
   pytest tests/ -v
   ```
