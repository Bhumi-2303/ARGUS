# ARGUS OIDC Trust Hardening, JWKS, & Frontend Security Verification

## 1. Executive Summary
This report validates the third major security milestone for ARGUS, focusing on OIDC cryptographic trust boundaries (JWKS caching and semantics), resilient SIEM delivery, frontend security remediation, and end-to-end access control regression testing. The scientific pipeline remained strictly uncompromised throughout.

## 2. Previous Security Baseline
ARGUS possessed strong deterministic execution boundaries, proper OIDC/JWT logic, and robust structural models. However, it lacked dynamic JWKS public-key caching (relying on static symmetric keys for testing), its SIEM integration lacked bounded retry logic, and the frontend improperly bundled API secrets as static `.env` environment variables.

## 3. JWKS Architecture
A thread-safe, timeout-bound `JWKSCache` was implemented in `src/argus/security/jwks.py`.
- **Key Retrieval:** `verify_token()` dynamically extracts the `kid` header and requests the key via the cache.
- **Lazy Refresh:** The cache refreshes if a `kid` is missing or the TTL expires.
- **Fallback Isolation:** If the JWKS endpoint is unavailable and the key is uncached, it gracefully returns `None`, yielding an HTTP 401 without crashing the event loop or silently authorizing the user.

## 4. Key Rotation Strategy
- **Behavior:** The `JWKSCache` maps `kid` directly to the active RSA key payload.
- **Rotation semantics:** When the Identity Provider rotates keys and signs a new token with an unknown `kid`, the cache intentionally misses, fetches the latest `/jwks.json`, updates its in-memory map lock, and successfully validates the new token seamlessly.

## 5. JWT Verification Security
`verify_token` enforces `verify_signature`, `verify_exp`, `verify_nbf`, `verify_iss`, and `verify_aud`. The `PyJWT` backend will refuse weak algorithms or algorithms outside the explicitly passed `oidc_algorithms` allowlist (e.g. `RS256`).

## 6. JWKS Failure Semantics
- **Cached Valid Key + Endpoint Unavailable:** Uses the cache (TTL valid).
- **Unknown Kid + Endpoint Available:** Fetches the new `kid` dynamically.
- **Unknown Kid / Expired + Endpoint Unavailable:** Returns `None`, JWT validation fails (HTTP 401).
- **Malformed / Empty JWKS:** Returns `None`, JWT validation fails.
Failure NEVER cascades into arbitrary token acceptance.

## 7. SIEM Reliability
The `AuditSink` class in `src/argus/security/sink.py` was rebuilt to encompass reliability semantics:
- **Local persistence:** Structlog locally records every event synchronously, guaranteeing local audibility.
- **Reliable remote dispatch:** An `asyncio.create_task()` daemon executes `_reliable_send_to_siem` featuring a 3-attempt bounded retry with exponential backoff on network failures. 
- **Fatal Error Isolation:** A 4xx SIEM error (excluding 429) terminates retries to prevent network storming. A complete SIEM outage never crashes the main FastAPI event loop.

## 8. Frontend Dependency Security
The NPM environment tree was successfully aligned. Extant vulnerabilities documented previously (e.g. `postcss`, `brace-expansion`, `nanoid`) affect the build pipeline (Vite, Tailwind) exclusively rather than production runtime code. 
- *Remediation Plan:* Scheduled patch-level bumps of the Vite/Tailwind ecosystem, averting mass upgrades that could compromise UI rendering.

## 9. Frontend Code Security
- **Finding:** `frontend/src/services/api.ts` was injecting a static `VITE_API_TOKEN` via `import.meta.env`, improperly leaking static secrets into the client build map.
- **Remediation:** Removed the static injection. It now dynamically retrieves the token via `localStorage.getItem('argus_token')` or `sessionStorage`. 
- **Verification:** The backend correctly blocks unauthorized API access (HTTP 403) regardless of any frontend DOM manipulation attempting to circumvent roles.

## 10. Authentication/RBAC Regression Results
The regression test suite (`test_rbac_oidc.py`) executed flawlessly:
- Correctly blocked tokens with invalid issuers and mismatched audiences.
- Correctly halted execution of `response:approve` by `VIEWER` identities.
- Logged exact `AUTHORIZATION_DENIED` semantics to the `AuditSink`.

## 11. End-to-End Security Test
A full E2E scenario was engineered in `tests/security/test_e2e_security.py`. It validated that:
1. `INCIDENT_RESPONDER` approves the workflow, returning HTTP 200.
2. An exact `RESPONSE_APPROVED` audit trace is instantiated inside the `AuditSink`, capturing the actor identity.
3. The deterministic backend operates irrespective of potential LLM anomalies.

## 12. CI/CD Security
`test_jwks_siem.py` and `test_e2e_security.py` are executed identically via the existing GitHub Actions `security-scan` job without modification, preserving pipeline integrity.

## 13. Deployment Security
- The Docker compose orchestrator maps only necessary ports.
- Configuration variables (`OIDC_ISSUER`, `JWKS_URL`) correctly source dynamically from `.env`.
- Internal services safely rely on `argus-network` bridge isolation.

## 14. Remaining Risks
- Frontend build-time library versions require long-term manual updating. 
- The OIDC mechanism currently trusts the network DNS of the provided `JWKS` string natively without mTLS anchoring.

## 15. Scientific Integrity Verification
Verified via `git diff`. The `artifacts/`, `models/`, and `src/argus/agents` evaluation cores remained frozen. The system enforces zero modifications against experimental predictions.

## 16. Final Readiness Matrix

| Capability | Status | Evidence | Remaining Requirement |
|------------|--------|----------|-----------------------|
| JWKS Management | IMPLEMENTED | `jwks.py`, Pytest cache hits | None |
| SIEM Reliability | IMPLEMENTED | `sink.py`, Backoff semantics | Configure endpoint |
| Client Auth Sec | IMPLEMENTED | Removed `.env` tokens | None |
| RBAC Integrity | IMPLEMENTED | E2E Pytests Passing | None |
| Sci Freeze | VERIFIED | `git diff --stat` | None |

## 17. Recommended Next Milestone
- Perform enterprise stress testing (Chaos Engineering) on Kafka telemetry processing and model throughput.
- Enforce strict Content Security Policy (CSP) headers on the frontend.
