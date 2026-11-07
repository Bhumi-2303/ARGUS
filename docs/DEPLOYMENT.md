# ARGUS Production Deployment Runbook

Comprehensive deployment guide for running ARGUS on **Oracle Cloud Always Free ARM (Ampere A1)** with **Caddy automatic TLS**, and **Cloudflare Pages** for the frontend SPA.

---

## 1. Architecture Overview

```
 [Users / Browsers]
         │
         ├───► HTTPS ────► [ Cloudflare Pages ] (Static SPA / web/dist)
         │                     │
         │                     ▼ API / WSS
         └───► HTTPS/WSS ─► [ Oracle Cloud Free ARM VM (2 OCPU / 12 GB) ]
                               │
                               ▼
                       ┌──────────────────────────────────────────────┐
                       │  Caddy Reverse Proxy (Port 80/443)           │
                       │  - Automatic TLS 1.3 (ZeroSSL / Let's Encrypt)│
                       │  - Rate limiting & Transport Security        │
                       └──────────────────────┬───────────────────────┘
                                              │ http://argus-platform:8000
                                              ▼
                       ┌──────────────────────────────────────────────┐
                       │  ARGUS Container (argus-platform:latest)     │
                       │  - Multi-arch (linux/arm64 & linux/amd64)    │
                       │  - Hardened non-root (UID 10001)             │
                       │  - Read-only FS with tmpfs /tmp              │
                       │  - 6-Agent Detection & Replay Pipeline       │
                       │  - Integrity Verification on Startup         │
                       └──────────────────────────────────────────────┘
```

---

## 2. Free-Tier Limits Checklist (Re-Check Before Deploying)

Before deploying, verify current resource quotas in the Oracle Cloud Infrastructure (OCI) console and Cloudflare dashboard:

| Provider | Resource / Quota | Always Free Limit | Recommended ARGUS Allocation | Verification Command / Check |
|---|---|---|---|---|
| **Oracle Cloud** | Compute Architecture | Ampere A1 (ARM64) | 1 VM: 2 OCPU, 12 GB RAM | `oci compute instance list` (OCI CLI) |
| **Oracle Cloud** | Max ARM Free Capacity | 4 OCPUs, 24 GB RAM | Uses 50% of free ARM capacity | Verify availability domain capacity |
| **Oracle Cloud** | Boot Volume | 200 GB total free | 50 GB Boot Volume (Balanced Tier) | Ensure total volume storage $\le$ 200 GB |
| **Oracle Cloud** | Public Egress Bandwidth| 10 TB / month free | $\approx$ 10–50 GB / month | Check billing alarms in OCI Cost Analysis |
| **Oracle Cloud** | Static Public IPv4 | 1 Free Ephemeral / Reserved IPv4 | 1 Reserved Public IPv4 | Attach reserved IP to VNIC |
| **Oracle Cloud** | VCN Security List | Stateful Ingress Rules | TCP 80, TCP 443 permitted | Verify VCN Security List & OS iptables |
| **Cloudflare** | Cloudflare Pages | Unlimited bandwidth, 500 builds/mo | 1 Production deployment | Cloudflare Dashboard > Workers & Pages |

> [!IMPORTANT]
> **Oracle Cloud ARM Availability**: In select OCI regions (e.g. `us-ashburn-1`, `eu-frankfurt-1`), Ampere A1 shapes may occasionally report "Out of capacity". If encountered, either retry in a different Availability Domain or submit via the OCI CLI loop.

> [!WARNING]
> **OCI Virtual Cloud Network (VCN) Firewall Rules**: By default, Oracle Linux and Ubuntu images on OCI include local `iptables` / `nftables` rules that block incoming traffic even if permitted by the VCN Security List. You must run:
> ```bash
> sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
> sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
> sudo netfilter-persistent save  # on Ubuntu/Debian
> ```

---

## 3. Model Artifacts Shipping & Startup Verification

To prevent repository bloat, large machine learning weights are managed as release assets or stored in object storage rather than tracked directly in git history.

### Cryptographic Integrity Verification

Every model artifact loaded by ARGUS is strictly validated at application startup against `artifacts/models/INTEGRITY_MANIFEST.json`:

```json
{
  "_format": "{ model_identifier: { artifact_path: relative_path, sha256: hex_digest } }",
  "model_d1_baseline": {
    "artifact_path": "artifacts/models/model_d1_baseline.txt",
    "sha256": "7f9a8ccc22e3d0c5f8ee45d536cf161a02cf8d9b00a4901db41d1a908f510b7b"
  },
  "model_d2_coral": {
    "artifact_path": "artifacts/models/model_d2_coral.txt",
    "sha256": "c71055c80df00fd887c21d052dadf1bb20f6596bc9f1ed9490b6107ddbe0ec28"
  },
  "model_d3_native": {
    "artifact_path": "artifacts/models/model_d3_native.txt",
    "sha256": "0dcac73c8655cca3f1a7a5c6df73836a0d5c4ad1d882fab2676b2e32f8bfc21c"
  },
  "xgb_adapted": {
    "artifact_path": "artifacts/models/xgb_adapted.json",
    "sha256": "6697c214a3c83fb1422f15fee34a89f2d320a95d28f8036768f01fb513e78a3d"
  }
}
```

1. **Startup Check**: `model_registry.load_all()` computes the SHA-256 checksum of every artifact before loading it into memory.
2. **Fail-Closed**: If any artifact hash does not match the manifest (due to tampering, truncation, or corruption), startup halts immediately with `SystemExit(1)`.
3. **Distribution Without Git Bloat**: In CI and production builds, model binaries can be downloaded from OCI Object Storage or GitHub Release Assets using `curl` and verified against the pre-committed `INTEGRITY_MANIFEST.json`.

---

## 4. Multi-Arch Container & Image Size Report

The multi-stage `Dockerfile` compiles cleanly for both `linux/amd64` and `linux/arm64` (aarch64).

### Building Multi-Arch Images
```bash
docker buildx create --use --name argus-builder
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t argus-platform:latest \
  --load .
```

### Container Image Footprint Breakdown

| Stage / Layer | Size | Purpose |
|---|---|---|
| Base OS (`python:3.11-slim`) | 128 MB | Minimal Debian Bookworm base |
| System Runtime (`libgomp1`, `curl`) | 18 MB | OpenMP runtime for LightGBM/XGBoost |
| Python Environment (`/opt/venv`) | 480 MB | Pre-compiled wheels (FastAPI, Scikit-learn, Shap, PyArrow) |
| Static Frontend (`web/dist`) | 3.2 MB | Pre-compiled Vite/React 19 bundle |
| Datasets & Models (`artifacts/`, `dataset/`) | 1.8 MB | Reference test sets, verified models, and CORAL parameters |
| **Total Uncompressed Image Size** | **~630 MB** | Full production container |
| **Compressed Registry Size** | **~210 MB** | Wire transfer size for fast VM pull |

---

## 5. Clean-Checkout-to-Public-URL Runbook

### Step 1: Provision Oracle Cloud ARM VM
1. Log in to the Oracle Cloud Console.
2. Navigate to **Compute > Instances > Create Instance**.
3. Shape: **Ampere VM.Standard.A1.Flex** (2 OCPU, 12 GB RAM).
4. Image: **Ubuntu 22.04 LTS** or **Oracle Linux 9 (aarch64)**.
5. Add your SSH public key.
6. Under Networking, assign a Public IPv4 Address.
7. Click **Create**.

### Step 2: Configure Firewall & DNS
1. In OCI Console: **Virtual Cloud Networks > Default Security List > Add Ingress Rule**:
   - Source CIDR: `0.0.0.0/0`
   - IP Protocol: `TCP`
   - Destination Port Range: `80,443`
2. Point your DNS A-records:
   - `api.yourdomain.com` $\to$ `<Oracle VM Public IP>`
   - `app.yourdomain.com` $\to$ CNAME to Cloudflare Pages (or managed in Cloudflare)

### Step 3: Clone Repository on VM
SSH into the Oracle VM:
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<ORACLE_VM_IP>
```

Clone the repository and install Docker:
```bash
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin git curl
sudo usermod -aG docker $USER
newgrp docker

# Clean checkout
git clone https://github.com/your-org/ARGUS.git /opt/argus
cd /opt/argus
```

### Step 4: Configure Production Environment
Copy the production environment template (never commit secrets):
```bash
cat << 'EOF' > .env
ENVIRONMENT=production
DOMAIN=api.yourdomain.com
ACME_EMAIL=admin@yourdomain.com
ARGUS_PORT=8000
ARGUS_ALLOWED_ORIGINS=https://app.yourdomain.com,https://api.yourdomain.com
EOF

chmod 600 .env
```

### Step 5: Start Caddy Reverse Proxy & Backend
Launch the production stack with automatic TLS, health checks, and log rotation:
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Verify container status:
```bash
docker compose -f docker-compose.prod.yml ps
```
Both `argus-platform` and `argus-caddy-proxy` will show `healthy` status.

### Step 6: Deploy Frontend to Cloudflare Pages
On your local machine or via GitHub Actions:
```bash
cd web
export VITE_API_BASE_URL=https://api.yourdomain.com
npm ci
npm run build

# Deploy via Wrangler CLI
npx wrangler pages deploy dist --project-name=argus-platform
```

Or configure Cloudflare Pages in the Cloudflare Dashboard:
- Framework preset: `Vite`
- Build command: `npm run build`
- Build output directory: `dist`
- Root directory: `web`
- Environment Variables:
  - `VITE_API_BASE_URL` = `https://api.yourdomain.com`

---

## 6. Post-Deployment Smoke Verification

Run the automated smoke test script against your public URL to verify `/health`, `/api/v1/agents/trace`, and WebSocket `/api/v1/stream`:

```bash
./scripts/smoke_test.sh https://api.yourdomain.com
```

### Expected Output:
```
=================================================================
ARGUS Post-Deployment Smoke Test
Target URL: https://api.yourdomain.com
Timestamp: 2026-11-05T12:00:00Z
=================================================================

[1/3] Testing /health endpoint...
Response: {"status":"healthy","version":"1.0.0"}
✓ /health check passed

[2/3] Testing /api/v1/agents/trace POST endpoint...
Response snippet: {"correlation_id":"flow-e3b1c","flow_status":"completed","total_events":6}...
✓ /api/v1/agents/trace execution passed

[3/3] Testing /api/v1/stream WebSocket endpoint...
Connecting to WebSocket: wss://api.yourdomain.com/api/v1/stream?domain=nfton&speed=50.0&seed=42
SUCCESS: Received handshake type=stream_init, label='verified flow replay'
✓ /api/v1/stream WebSocket check passed

=================================================================
ALL SMOKE TESTS PASSED (3/3)
=================================================================
```

---

## 7. Operations, Logs, and Rollback

### Log Inspection & Rotation
Docker log rotation is configured to max 10MB per file with 3–5 file retention. Inspect logs:
```bash
docker compose -f docker-compose.prod.yml logs --tail=100 -f argus-platform
docker compose -f docker-compose.prod.yml logs --tail=100 -f caddy
```

### Zero-Downtime Application Update
```bash
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build --remove-orphans
./scripts/smoke_test.sh https://api.yourdomain.com
```

### Rollback Procedure
If verification fails, rollback to the previous commit immediately:
```bash
git checkout <previous_commit_sha>
docker compose -f docker-compose.prod.yml up -d --build
```
