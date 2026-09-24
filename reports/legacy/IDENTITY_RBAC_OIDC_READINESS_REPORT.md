# ARGUS Identity, RBAC, and OIDC Readiness Report

## 1. Executive Summary
This report summarizes the second major security milestone for the ARGUS platform: implementing robust identity management, Role-Based Access Control (RBAC), OpenID Connect (OIDC) integration boundaries, and centralized SIEM audit capabilities. The implementation establishes rigorous authorization controls on high-impact incident response actions, without altering any underlying scientific functionality.

## 2. Previous Security Baseline
The previous security hardening phase correctly secured input boundaries (Pydantic validation), LLM isolation (PolicyEngine dominance), and basic authentication (JWT). However, it lacked enterprise integration capabilities for centralized identity (OIDC), granular authorization (RBAC), and centralized security monitoring (SIEM).

## 3. Current Authentication Architecture
- **JWT Validation:** Upgraded to support OIDC-compliant constraints (Issuer, Audience, Algorithms, Expiration, Not-Before, and necessary claims).
- **Flexibility:** Supports a hybrid local mode (`argus-local`) and an `oidc_enabled` configuration block for external Identity Providers (IdP).

## 4. RBAC Model
Introduced explicit server-side authorization boundaries aligned with standard SOC operations:
- **VIEWER**: `events:read`, `incidents:read`, `policy:read`, `audit:read`
- **ANALYST**: Incorporates VIEWER permissions + `incidents:update`, `response:request`
- **INCIDENT_RESPONDER**: Incorporates ANALYST permissions + `response:approve`, `events:write`, `incidents:close`
- **SECURITY_ADMIN**: `*` (full access), `system:admin`

## 5. OIDC Architecture
A clean provider-neutral OIDC integration boundary was designed inside `config/settings.py` and `src/argus/security/auth.py`. ARGUS does NOT store credentials or implement custom identity. Instead, it expects externally signed tokens from an OIDC Issuer.
- **Configurable properties**: `oidc_issuer`, `oidc_audience`, `oidc_algorithms`, `oidc_jwks_url`.

## 6. JWT Security
Strict validation logic enforces standard JSON Web Token profile restrictions:
- Rejects missing subjects or roles.
- Validates signature and cryptographic algorithms against an explicit allowlist.
- Rejects expired and audience-mismatched tokens.

## 7. Authorization Enforcement
- Replaced monolithic role checks with granular `require_permission(resource, action)` dependency injections across the FastAPI router `src/argus/api/routers/incidents.py`.
- LLM outputs remain isolated from the authorization resolution phase.

## 8. High-Impact Response Approval
- The endpoint `/incidents/{incident_id}/approve` now strictly requires `response:approve` permission (held by `INCIDENT_RESPONDER` or `SECURITY_ADMIN`).
- High-impact decisions automatically write an immutable `RESPONSE_APPROVED` event into the structured AuditSink.

## 9. Security Audit Event Architecture
Defined `SecurityAuditEvent` ensuring conformity for ingestion. Contains explicit tracking identifiers: `audit_event_id`, `actor_id`, `actor_type`, `action`, `resource`, `resource_id`, `outcome`, `reason`, `source_ip`.

## 10. SIEM Integration
Created a provider-neutral `AuditSink` in `src/argus/security/sink.py`:
- **Local Fallback:** Events persistently append to structured logs (`structlog`) to guarantee local auditability even under network isolation.
- **Remote Integration:** Supports async dispatch to external SIEM HTTP endpoints (e.g. Splunk HEC, MS Sentinel, Elastic) without blocking the primary HTTP event loop.

## 11. Frontend Authorization
Frontend Authorization was reviewed. The existing React deployment utilizes frontend route checks; however, API server-side authorization is fully detached and acts as the definitive security boundary.

## 12. Security Test Results
Created `tests/security/test_rbac_oidc.py` executing tests on:
- Missing authentication / Malformed tokens
- Expired tokens / Invalid signatures
- Wrong issuer / Wrong audience / Missing claims
- VIEWER role unable to approve incidents (HTTP 403)
- INCIDENT_RESPONDER role able to execute approvals
- Structured audit event emission upon authorization denial (`AUTHORIZATION_DENIED`)

## 13. CI/CD Changes
The previous `.github/workflows/ci.yml` pipeline (which includes security dependency scanning) inherently executes the new RBAC testing module via the `pytest tests/security/` stage.

## 14. Remaining Risks
- **Frontend Dependency Audit:** Known development-time vulnerabilities remain, requiring a scheduled manual bump.
- **Provider-Specific JWKS Fetching:** The OIDC validation currently relies on a symmetric key verification boundary rather than dynamically caching JWKS public keys.

## 15. Deployment Requirements
- A robust enterprise Identity Provider (e.g. Okta, Azure AD, Keycloak) must be provisioned.
- A centralized SIEM endpoint must be configured in `siem_endpoint`.

## 16. Scientific Integrity Verification
No alterations were performed on ML models, datasets, or predictive schemas. The research validity is fully maintained.

## 17. Final Readiness Matrix

| Capability | Status | Evidence | Remaining Requirement |
|------------|--------|----------|-----------------------|
| OIDC | IMPLEMENTED | `auth.py`, `settings.py` OIDC flags | Provision enterprise IdP |
| JWT Validation | IMPLEMENTED | Added exhaustive pyjwt validations | Asymmetric JWKS caching |
| Server-side RBAC | IMPLEMENTED | `authorization.py`, `incidents.py` | None |
| High-Impact Approval | IMPLEMENTED | `approve_incident` uses `response:approve` | None |
| Audit Events / SIEM | IMPLEMENTED | `sink.py`, `AuditLogger` async dispatch | Set up SIEM HEC endpoint |
| Scientific Integrity | IMPLEMENTED | `git diff --stat` confirms zero ML changes | None |

## 18. Recommended Next Milestone
- Implement dynamic JWKS public key caching for strict asymmetric OIDC token verification.
- Enact manual resolution of frontend React application dependencies and build tooling.
