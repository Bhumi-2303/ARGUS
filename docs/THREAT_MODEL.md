# ARGUS Threat Model & Security Analysis

## 1. System Scope & Primary Assets

The ARGUS platform protects Smart Grid (IEC 60870-5-104) and IoT network infrastructure. The primary assets requiring protection include:

1. **Inference & Decision Integrity**: Preventing adversaries from evading intrusion detection models or manipulating domain adaptation transforms (Clean Class-aware CORAL).
2. **Incident Response Safeguards**: Protecting the human-in-the-loop approval mechanism that authorizes physical SCADA grid mitigations.
3. **Forensic Audit Trails**: Maintaining non-repudiable logs of detection events, operator approvals, and model provenance.
4. **Platform Availability**: Ensuring continuous monitoring without vulnerability to resource exhaustion or denial-of-service.

---

## 2. Threat Actors & Capabilities

- **Nation-State / Advanced Persistent Threat (APT)**: Capable of sophisticated protocol-level attacks on SCADA protocols, feature perturbation, and evasion attacks.
- **Ransomware / Cybercriminal Group**: Seeks to compromise grid telemetry, pivot into control systems, or disable detection monitoring.
- **Compromised Insider / Rogue Operator**: Possesses valid network access; attempts unauthorized approvals or policy tampering.
- **Compromised Sensor / Edge Node**: Feeds malformed packets, extreme numerical values, or malicious telemetry payloads into the ingestion stream.

---

## 3. STRIDE Analysis & Mitigations

### 3.1. Spoofing
- **Threat**: Attacker creates forged JWT tokens with arbitrary claims or uses algorithm confusion (e.g. signing with an RSA public key using `HS256` or setting algorithm to `none`).
- **Mitigation**:
  - Authoritative OIDC/JWKS asymmetric signature verification (`RS256`, `ES256`).
  - Algorithm allowlist strictly rejects `HS*` and `none`.
  - Non-blocking JWKS caching with rate-limited key rotation.
  - Verification of `iss`, `aud`, `exp`, `nbf`, `iat`, and `kid`.

### 3.2. Tampering
- **Threat**: Tampering with ML model weights (`.txt`, `.json`), evaluation tables, or container source code.
- **Mitigation**:
  - `artifacts/manifest.json` SHA-256 hash verification at application startup.
  - Safe deserialization: PyTorch models loaded strictly with `weights_only=True`.
  - Container hardening: non-root user (`argususer:10001`), read-only container code layout (`chmod 550`), dropped capabilities (`cap_drop: ALL`).

### 3.3. Repudiation
- **Threat**: An operator denies approving an incident response action that caused a power disruption.
- **Mitigation**:
  - Approvals require explicit `approve:response` RBAC permission.
  - The approving identity is cryptographically derived from `user.sub` of the verified JWT.
  - Every approval generates an immutable `SecurityAuditEvent` recording `actor_id`, `source_ip`, `timestamp`, `incident_id`, and `reason`.

### 3.4. Information Disclosure
- **Threat**: Attacker extracts internal system paths, environment secrets, or server files via path traversal or stack trace error leakage.
- **Mitigation**:
  - Global error masking middleware intercepts all unhandled exceptions, returning standard `internal_server_error` envelopes with correlation `request_id`.
  - Zero stack traces or file paths returned to clients.
  - Strict path traversal defenses (`_resolve_safe_path`, `is_relative_to`) in `DataManager` and SPA static handlers.
  - Strict table and domain name allowlists (`ALLOWED_TABLES`, `ALLOWED_DOMAINS`).

### 3.5. Denial of Service
- **Threat**: Flooding API with massive payloads, opening unbounded WebSocket connections, or sending malformed telemetry vectors.
- **Mitigation**:
  - 1 MB strict request size limit (`max_request_size_bytes = 1,048,576`).
  - Rate limiting (token-bucket / sliding window) per client IP.
  - WebSocket idle timeouts (`websocket_idle_timeout_seconds = 60`) and max connection lifetime limits (`3600s`).
  - Stream duration and row bounds (`MAX_STREAM_ROWS = 1000`, `MAX_STREAM_DURATION = 300s`).

### 3.6. Elevation of Privilege
- **Threat**: An unprivileged viewer escalates privileges to trigger predictions, explainability, or incident actions.
- **Mitigation**:
  - Fine-grained FastAPI dependency checks (`require_permission`) on every versioned endpoint.
  - Missing permissions immediately return `403 Forbidden` and log a security audit event.

---

## 4. Machine Learning & Agent Threat Analysis

### 4.1. Adversarial Evasion & NaN/Inf Ingestion
- **Attack Vector**: Supplying `NaN`, `Infinity`, or extremely large floats to crash inference pipelines or trigger undefined model behavior.
- **Defense**: Strict Pydantic v2 validation with `allow_inf_nan=False`, finite bounds (`ge=0.0`, `le=1000.0`), and schema enforcement.

### 4.2. Covariate Shift & Protocol Blindspots
- **Attack Vector**: Protocol divergence between training and deployment domains (e.g. SCADA IEC-104 domain shift).
- **Defense**: Continuous Kolmogorov-Smirnov (KS) two-sample testing and Population Stability Index (PSI) monitoring.

### 4.3. Prompt Injection on Agent LLM Stubs
- **Attack Vector**: Injecting malicious system instructions through flow telemetry summaries.
- **Defense**: Deterministic Policy Engine evaluation contracts. The policy engine evaluates deterministic rules based on verified detector outputs and asset criticality, ignoring untrusted free-form prompt modifications.
