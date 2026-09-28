# ARGUS Security Policy & Architecture

## Security Overview

The **Autonomous Risk-aware Grid Understanding & Security (ARGUS)** platform is an AI-powered cybersecurity system designed for Smart Grid and Industrial Control System (ICS/SCADA) infrastructure. Given its mission-critical domain, the system enforces a strict **defense-in-depth, fail-closed security posture**.

---

## 1. Vulnerability Reporting

If you identify a security vulnerability in ARGUS, please report it privately:

- **Security Team Email**: `security@argus-platform.io`
- **PGP Key**: Fingerprint `A1B2 C3D4 E5F6 7890 1234 5678 9ABC DEF0 1234 5678`
- **Response SLA**: Initial triage within 24 hours; critical fix target within 72 hours.
- **Coordinated Disclosure**: We request reporters adhere to coordinated disclosure principles until mitigations are released.

---

## 2. Authentication Architecture

ARGUS uses standard, provider-neutral **OpenID Connect (OIDC) and OAuth 2.0 JWT** authentication:

- **Validation Enforcement**:
  - Cryptographic signatures verified against upstream JSON Web Key Sets (JWKS).
  - Supported Asymmetric Algorithms: `RS256`, `ES256` (HMAC `HS*` and `none` are strictly rejected to prevent algorithm confusion).
  - Strict Token Claims: `exp` (expiration), `nbf` (not before), `iat` (issued at), `iss` (issuer), `aud` (audience), and `kid` (key ID).
- **JWKS Client Resiliency**:
  - Non-blocking asynchronous retrieval via `httpx.AsyncClient`.
  - 5-second HTTP connect and read timeout.
  - In-memory key caching with 1-hour TTL.
  - Rate-limited key rotation on `kid` cache misses (maximum 1 remote refresh per 60 seconds).
  - Fail-closed behavior: If JWKS retrieval fails and no cached key exists, incoming requests are rejected with `401 Unauthorized`.
- **Fail-Closed Production Gate**:
  - When `ENVIRONMENT=production`, the application refuses to start if `OIDC_ENABLED=False`, if placeholder secrets are detected, if insecure symmetric algorithms are specified, or if non-HTTPS JWKS endpoints are configured.

---

## 3. Role-Based Access Control (RBAC)

Authentication verifies identity; explicit authorization verifies actions. ARGUS enforces fine-grained permission checks across all API routers:

| Permission | Description | Target Endpoints | Roles |
|---|---|---|---|
| `read:domains` | View registered telemetry domains & metadata | `GET /api/v1/domains` | Viewer, Analyst, Operator, Admin |
| `read:models` | View model registry & deployment status | `GET /api/v1/models` | Viewer, Analyst, Operator, Admin |
| `read:results` | Access verified evaluation tables | `GET /api/v1/results/{table}` | Viewer, Analyst, Operator, Admin |
| `read:telemetry` | View sample flows and live telemetry streams | `GET /api/v1/data/*`, `GET /api/v1/stream` | Analyst, Operator, Admin |
| `read:agent-topology` | View multi-agent topology & connect to WS stream | `GET /api/v1/agents/topology`, `WS /api/v1/agents/stream` | Analyst, Operator, Admin |
| `read:monitoring` | View drift alerts & telemetry metrics | `GET /api/v1/monitoring/*` | Analyst, Operator, Admin |
| `read:incidents` | View incidents & audit timeline | `GET /api/v1/incidents/*` | Operator, Admin |
| `run:prediction` | Execute live inference | `POST /api/v1/predict` | Analyst, Operator, Admin |
| `run:explanation` | Compute SHAP feature attributions | `POST /api/v1/explain` | Analyst, Operator, Admin |
| `run:onboarding` | Trigger domain adaptation simulation | `POST /api/v1/onboard` | Analyst, Admin |
| `run:agent-trace` | Trigger synthetic multi-agent evaluation | `POST /api/v1/agents/trace` | Operator, Admin |
| `write:incidents` | Create or transition incident lifecycle | `POST /api/v1/incidents`, `PATCH /status` | Operator, Admin |
| `approve:response` | Human-in-the-loop incident mitigation approval | `POST /api/v1/incidents/{id}/approve` | Operator, Admin |

### Human-in-the-Loop Approval Auditing
Approvals require the explicit `approve:response` permission. The approving actor is cryptographically bound to `user.sub` from the verified JWT principal and durably logged to the security audit trail.

---

## 4. Input Validation & Numeric Sanitization

- **Strict Pydantic v2 Models**:
  - `allow_inf_nan=False` enforced across all feature models (`FeatureInput`, `PredictRequest`, `ExplainRequest`).
  - Finite bounds: feature values bounded (`ge=0.0`, `le=1000.0` or `le=100.0`).
  - Window sizes bounded (`ge=10`, `le=50000`).
  - String regex allowlists: `pattern=r"^[a-zA-Z0-9_-]+$"` on domain and model identifiers.
- **Request Size Limiting**:
  - Maximum body size enforced at 1 MB (`1,048,576` bytes).
  - Payloads exceeding the limit receive `413 Payload Too Large`.

---

## 5. Defense-in-Depth HTTP Headers & CORS

Every HTTP response from ARGUS includes defensive security headers:

- `Content-Security-Policy`: Restricts scripts and styles to `'self'`, forbids plugins (`object-src 'none'`), and prevents framing (`frame-ancestors 'none'`).
- `X-Frame-Options: DENY`: Blocks clickjacking attacks.
- `X-Content-Type-Options: nosniff`: Prevents browser MIME-type sniffing.
- `Referrer-Policy: strict-origin-when-cross-origin`: Minimizes referrer leakage.
- `Permissions-Policy`: Disables sensitive browser APIs (`geolocation=()`, `microphone=()`, `camera=()`, `usb=()`).
- `Strict-Transport-Security`: Enforces HTTPS in production (`max-age=31536000; includeSubDomains; preload`).

CORS is strictly configured:
- In production, wildcard `*` and `localhost` origins are forbidden.
- Allowed origins must match configured production domains exactly.

---

## 6. Information Disclosure Prevention & Error Masking

- **Error Masking**: Unhandled exceptions (`500`) return a generic JSON envelope:
  ```json
  {
    "error": "internal_server_error",
    "message": "An unexpected error occurred. Please contact the administrator with the correlation request ID.",
    "request_id": "req-a1b2c3d4e5f6"
  }
  ```
- **Zero Stack Traces**: Python tracebacks, file paths (`/app/...`, `/usr/...`), and internal variable state are never returned to clients.
- **Structured Logging**: Full stack traces are correlated with `request_id` and logged securely to the server-side audit sink.

---

## 7. Model & Artifact Integrity

- **Authoritative Hash Verification**: Model weights, evaluation CSVs, and sample datasets are indexed in `artifacts/manifest.json` with SHA-256 digests.
- **Startup Integrity Checks**: The system validates files against the manifest at boot.
- **Safe Deserialization**: PyTorch models are strictly loaded with `weights_only=True`. Insecure Python `pickle.load` of untrusted files is prohibited.
