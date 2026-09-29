# ARGUS — Autonomous Risk-aware Grid Understanding & Security

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://python.org)
[![Backend Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Frontend Stack](https://img.shields.io/badge/Frontend-React%2019%20%7C%20Vite%20%7C%20Three.js%20%7C%20TailwindCSS-61DAFB.svg)](https://react.dev)
[![Test Suite](https://img.shields.io/badge/Tests-100%25%20Passing-success.svg)](tests/)
[![Security](https://img.shields.io/badge/Security-Hardened%20(OIDC%20%7C%20RBAC%20%7C%20CSP)-brightgreen.svg)](docs/SECURITY.md)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**ARGUS** is an autonomous cyber-physical defense platform engineered for **Industrial Control Systems (ICS)**, **SCADA networks**, and **Smart Grid Infrastructure**. It investigates and resolves **cross-domain transfer failure and representation collapse** in network intrusion detection under strict zero-leakage protocols.

ARGUS combines a **leakage-controlled domain adaptation model** (Class-Aware CORAL + XGBoost) with a **real-time 6-agent autonomous execution pipeline**, offering end-to-end telemetry ingestion, threat classification, TreeSHAP explainability, MITRE ATT&CK ICS context retrieval, operational risk scoring, and automated decision playbooks.

---

## 📌 Executive Summary & Key Research Findings

1. **Cross-Domain Generalization Collapse**: Models trained on enterprise IoT traffic (**CICIoT2023 / D1**) achieve $>97\%$ in-domain F1, but catastrophically collapse to near-chance or majority-class predictions when evaluated across domains on smart home IoT (**NF-ToN-IoT-v2 / D2**) and industrial SCADA (**IEC 60870-5-104 / D3**).
2. **Clean Class-Aware CORAL is the Leakage-Controlled Winner**:
   - Aligning class-conditional second-order statistics on target adaptation splits (without touching test labels) and calibrating decision thresholds ($\tau^* = 0.99$) on disjoint calibration splits achieves:
     - **Balanced Accuracy**: $71.09\%$
     - **Matthews Correlation Coefficient (MCC)**: $+0.3855$
     - **Precision**: $94.00\%$
     - **Specificity**: $91.43\%$
3. **Domain-Adversarial Neural Network (DANN) Degeneracy**:
   - Evaluated against raw prediction exports ($N = 2,627,177$), DANN achieves $\text{ROC-AUC} = 0.3321$ and $\text{Specificity} = 0.06\%$, demonstrating complete collapse into majority-class prediction rather than domain invariance.
4. **Representation Resolution Drives Transfer Feasibility**:
   - Extending compact 4-feature representations to SCADA traffic (D3) fails non-monotonically (an 8-feature representation collapses to $\text{ROC-AUC} = 0.445$).
   - Only D3's native 70-feature flow representation restores non-trivial discriminability ($\text{ROC-AUC} = 0.6744$).

---

## 🏗️ Multi-Agent Architecture & Pipeline

ARGUS executes an autonomous, sequential 6-agent pipeline with a shared, strictly typed `PipelineContext`. If any upstream agent encounters an unrecoverable failure, downstream dependencies are marked as `SKIPPED` rather than producing fabricated results.

```text
       [ Telemetry Ingress (API Gateway / CSV / Stream) ]
                               │
                               ▼
                    [ Event Message Bus ]
                               │
                               ▼
                     [ Orchestrator Engine ]
                               │
   ┌───────────────────────────┴───────────────────────────┐
   │                                                       │
   ▼                                                       │
1. DATA INTELLIGENCE AGENT (DIA)                           │
   • Harmonized 4-feature extraction                       │
   • Bounds validation & zero-value preservation           │
   │                                                       │
   ▼                                                       │
2. THREAT ANALYSIS AGENT (TAA)                             │
   • D1->D2 CORAL XGBoost model inference                  │
   • Calibrated decision threshold (τ* = 0.99)             │
   • Attack probability & threat level rating              │
   │                                                       │
   ▼                                                       │
3. EXPLAINABILITY AGENT (EA)                               │
   • Exact TreeSHAP feature attributions                   │
   • Attribution polarity & ranking                        │
   │                                                       │
   ▼                                                       │
4. KNOWLEDGE CONTEXT AGENT (KCA)                            │
   • MITRE ATT&CK for ICS technique mapping                │
   • CISA Known Exploited Vulnerabilities lookup           │
   • Affected asset & CVE contextualization                │
   │                                                       │
   ▼                                                       │
5. RISK PREDICTION AGENT (RPA)                             │
   • Asset criticality evaluation                          │
   • Cascading impact estimation & trend analysis          │
   • Multi-factor operational risk scoring (0-100)         │
   │                                                       │
   ▼                                                       │
6. DECISION SUPPORT AGENT (DSA)                            │
   • Deterministic mitigation playbook selection           │
   • Action prioritization & human operator approvals      │
   └───────────────────────────┬───────────────────────────┘
                               │
                               ▼
        [ Full Execution Trace & Live 3D/2D Visualizer ]
```

### The 6 Autonomous Agents in Detail

| # | Agent Name | Core Responsibilities & Tools | Input $\to$ Output |
| :---: | :--- | :--- | :--- |
| **1** | **Data Intelligence Agent** | • Validates raw telemetry chunks against strict feature bounds.<br>• Extracts 4 harmonized flow features: `pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`.<br>• Preserves zero values and rejects NaNs/Infs. | Raw Network Flow $\to$ `ExtractedFeatures` |
| **2** | **Threat Analysis Agent** | • Executes domain-adapted model (`model_d2_coral` / `xgb_adapted`).<br>• Evaluates prediction against calibrated threshold $\tau^* = 0.99$.<br>• Generates calibrated attack probability and classified threat level. | `ExtractedFeatures` $\to$ `ThreatAnalysisResult` |
| **3** | **Explainability Agent** | • Computes exact TreeSHAP attributions using background reference distributions.<br>• Identifies driving features causing malicious vs. benign classification.<br>• Performs target-gain disconnect verification. | `ThreatAnalysisResult` $\to$ `ExplanationResult` |
| **4** | **Knowledge Context Agent** | • Maps detected threat signatures to MITRE ATT&CK for ICS matrices.<br>• Queries CISA ICS advisories and CVE vulnerability databases.<br>• Enriches telemetry with OT protocol context (Modbus, DNP3, IEC-104). | `ExplanationResult` $\to$ `EnrichmentContext` |
| **5** | **Risk Prediction Agent** | • Assesses asset criticality (`CriticalAssetAnalyzer`).<br>• Computes grid impact & operational disruption (`ImpactEstimator`).<br>• Evaluates escalation trends (`TrendAnalyzer`).<br>• Computes deterministic risk score: $R = \text{round}(\text{Criticality} \times \text{Threat} \times \text{Impact} \times 100)$. | `EnrichmentContext` + `Threat` $\to$ `RiskEvent` |
| **6** | **Decision Support Agent** | • Matches incident profile to ICS containment playbooks (`PlaybookSelector`).<br>• Generates prioritized mitigation actions (`ActionPrioritizer`).<br>• Prepares human-in-the-loop operator approval tokens (`ApprovalGenerator`). | `RiskEvent` $\to$ `DecisionAnalysisResult` |

---

## 📊 Authoritative Empirical Results

All experimental numbers backing the research are frozen and cryptographically verifiable in [`results/verified/`](results/verified/):

### D1 (CICIoT2023) $\to$ D2 (NF-ToN-IoT-v2) Cross-Domain Benchmark ($N = 2,627,177$)

| Model | Decision $\tau$ | Accuracy | Precision | Recall | F1 | Balanced Acc. | Specificity | MCC | ROC-AUC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Clean Class-Aware CORAL + XGBoost** | **0.99** | **0.6191** | **0.9400** | 0.5076 | 0.6592 | **0.7109** | **0.9143** | **+0.3855** | 0.5970 | **Verified Winner** |
| Source-Only XGBoost | 0.50 | 0.7207 | 0.7247 | 0.9919 | 0.8375 | 0.4972 | 0.0025 | -0.0311 | 0.3230 | Unadapted Baseline |
| Global CORAL + XGBoost | 0.50 | 0.6347 | 0.7013 | 0.8652 | 0.7747 | 0.4448 | 0.0244 | -0.1610 | 0.2852 | Marginal Alignment Only |
| DANN | 0.60 | 0.7259 | 0.7259 | 0.9998 | 0.8412 | 0.5002 | 0.0006 | +0.0129 | 0.3321 | Majority-Class Collapse |
| *Diagnostic Class-Aware CORAL* | *0.50* | *0.5506* | *0.7262* | *0.6113* | *0.6638* | *0.5006* | *0.3899* | *+0.0011* | *0.6361* | *Diagnostic (Used Target Test Labels)* |

All model weights are verified against [`artifacts/models/INTEGRITY_MANIFEST.json`](artifacts/models/INTEGRITY_MANIFEST.json).

---

## 📁 Consolidated Datasets (`dataset/` or `datasets/`)

All dataset files needed for live demos, model predictions, evaluation, and automated testing are centralized in `dataset/` (accessible via `datasets` symlink as well):

| File | Description | Target Use Case |
| :--- | :--- | :--- |
| `dataset/sample_attack_flow.csv` | Curated malicious network flow (DoS / brute-force attack signature). | Drag-and-drop into UI or CLI curl to verify attack detection |
| `dataset/sample_benign_flow.csv` | Normal operational network flow. | Drag-and-drop into UI or CLI curl to verify benign baseline |
| `dataset/ciciot_sample.csv` | 100 benchmark sample flows from CICIoT2023 (Source Domain). | Batch evaluation |
| `dataset/nfton_sample.csv` | 100 benchmark sample flows from NF-ToN-IoT-v2 (Target Domain). | Batch evaluation under domain shift |
| `dataset/ciciot.parquet` | 10,000 verified rows from CICIoT2023. | Backend sample API & distribution comparison |
| `dataset/nfton.parquet` | 10,000 verified rows from NF-ToN-IoT-v2. | Backend sample API & distribution comparison |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.11, 3.12, or 3.14
- Node.js 18+ and npm (for frontend compilation)

### 2. Environment Setup

```bash
# Clone the repository
git clone https://github.com/Bhumi-2303/ARGUS.git
cd ARGUS

# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies in editable mode
pip install -e .[dev,test]
```

### 3. Launch Live Demo (Single Command)

The unified demo runner serves both the FastAPI REST/WebSocket backend and the compiled React dashboard on **`http://localhost:8000`**:

```bash
make demo
```

Once running:
- **Web Dashboard**: Open [http://localhost:8000](http://localhost:8000)
- **Multi-Agent 3D/2D Topology**: Open [http://localhost:8000/topology](http://localhost:8000/topology)
- **Interactive OpenAPI Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: Open [http://localhost:8000/health](http://localhost:8000/health)

### 4. Running Verification Tests

Run the full end-to-end and security test suite:

```bash
# Run real multi-agent pipeline integration tests
pytest tests/e2e/test_real_pipeline.py

# Run security headers & CORS tests
pytest tests/security/test_security_headers_and_cors.py

# Run startup asset and numerical integrity checks
python scripts/startup_check.py
python scripts/verify_ui_numbers.py
```

---

## 🖥️ Live Web Dashboard Walkthrough

| Page Route | Title | What it Visualizes |
| :--- | :--- | :--- |
| **`/topology`** | **Multi-Agent Processing** | Dynamic 3D WebGL / 2D SVG topology graph showing all 10 nodes and 8 edges. Includes the **"Trigger Real Flow"** button, live WebSocket event trace log, and agent execution matrix with genuine execution durations and outputs. |
| **`/input`** | **Input & Prediction** | Interactive flow inspection. Select pre-loaded verified samples or drag-and-drop custom CSV files (`dataset/sample_attack_flow.csv`). Triggers the full real multi-agent backend and displays the resulting threat, risk, and recommendations. |
| **`/explain`** | **Explanation & Visualization** | Visualizes exact TreeSHAP feature attributions for any flow, comparing model feature importance between source and adapted domains. |
| **`/results`** | **Results & Evaluation** | Verified side-by-side performance benchmarks, ROC-AUC comparison tables, and domain shift statistics (KS drift, PSI). |
| **`/`** | **System Overview** | Core empirical findings, research narrative, transfer failure mechanisms, and platform limitations. |

---

## 💻 CLI Real Pipeline Inference Example

You can execute the entire 6-agent pipeline directly via curl:

```bash
curl -X POST "http://localhost:8000/api/v1/agents/trace" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "pkt_mean_to_max": 0.99,
      "tcp_flag_density": 0.95,
      "log_pkt_mean": 8.5,
      "log_pkt_max": 9.1
    },
    "model_name": "model_d2_coral"
  }'
```

**Output response includes the full sequential trace:**
```json
{
  "correlation_id": "flow-d3a9ef1e",
  "flow_status": "completed",
  "total_events": 8,
  "events": [
    { "source_node": "api_gateway", "target_node": "message_bus", "summary": "Received simulation request." },
    { "source_node": "message_bus", "target_node": "orchestrator", "summary": "Orchestrator began execution." },
    { "source_node": "orchestrator", "target_node": "data_intelligence", "summary": "DATA_INTELLIGENCE: SUCCESS — features: 4 total" },
    { "source_node": "data_intelligence", "target_node": "threat_analysis", "summary": "THREAT_ANALYSIS: SUCCESS — threat_level=high, confidence=0.8920" },
    { "source_node": "threat_analysis", "target_node": "explainability", "summary": "EXPLAINABILITY: SUCCESS — top_feature=pkt_mean_to_max" },
    { "source_node": "explainability", "target_node": "knowledge_context", "summary": "KNOWLEDGE_CONTEXT: SUCCESS — mitre=1, cves=2" },
    { "source_node": "knowledge_context", "target_node": "risk_prediction", "summary": "RISK_PREDICTION: SUCCESS — risk=78, sev=HIGH" },
    { "source_node": "risk_prediction", "target_node": "decision_support", "summary": "DECISION_SUPPORT: SUCCESS — recs=3, pri=1" }
  ]
}
```

---

## 🔒 Security & Defensive Architecture

- **Content Security Policy (CSP)**: Strict directives including `worker-src 'self' blob:` and `child-src 'self' blob:` to safely accommodate 3D WebGL workers without compromising defense-in-depth.
- **OWASP Defensive Headers**: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, and sensitive endpoint `Cache-Control: no-store`.
- **Role-Based Access Control (RBAC)**: Fine-grained permissions (`read:agent-topology`, `execute:flow-simulation`) backed by JWT validation.
- **Model Tamper Resistance**: All model artifact hashes are verified against [`INTEGRITY_MANIFEST.json`](artifacts/models/INTEGRITY_MANIFEST.json) upon server startup.

---

## 📁 Repository Directory Structure

```text
ARGUS/
├── README.md                      # Master project architecture & guide
├── Makefile                       # Single-command setup, demo, test, and build targets
├── pyproject.toml                 # Unified package configuration & dependencies
├── dataset/                       # Centralized datasets (sample CSVs, parquets, raw links)
│   ├── sample_attack_flow.csv     # Demo attack flow CSV
│   ├── sample_benign_flow.csv     # Demo benign flow CSV
│   ├── ciciot.parquet             # 10k verified source samples
│   ├── nfton.parquet              # 10k verified target samples
│   └── README.md                  # Dataset usage guide
├── artifacts/
│   └── models/                    # Verified model weights & INTEGRITY_MANIFEST.json
├── configs/                       # Configuration YAMLs and settings definitions
├── results/
│   ├── verified/                  # Authoritative CSV benchmarks & publication tables
│   └── diagnostic/                # Exploratory ablation studies
├── scripts/
│   ├── start_demo.py              # Unified single-port demo server
│   ├── startup_check.py           # Pre-flight asset and model integrity verification
│   └── verify_ui_numbers.py       # Ground-truth API-to-CSV verification
├── src/argus/
│   ├── agents/                    # The 6 autonomous agents (DIA, TAA, EA, KCA, RPA, DSA)
│   ├── orchestrator/              # Real execution pipeline and shared context engine
│   ├── api/                       # FastAPI v1 REST & WebSocket routers
│   ├── auth/                      # RBAC, JWT validation, and security audit loggers
│   ├── security/                  # HTTP security headers, CSP, and defensive middleware
│   ├── registry/                  # Model registry and metadata catalog
│   └── shift/                     # Distribution shift analytics (KS-test, PSI)
├── tests/
│   ├── e2e/                       # End-to-end multi-agent execution pipeline tests
│   ├── security/                  # CSP, CORS, RBAC, and adversarial verification tests
│   └── agents/                    # Dedicated test suites for each individual agent
└── web/                           # Production React 19 + TypeScript + Three.js frontend
    ├── src/
    │   ├── features/topology/     # 3D WebGL / 2D SVG agent architecture visualizer
    │   ├── features/analysis/     # Input & live prediction dashboard
    │   ├── features/explain/      # TreeSHAP feature attributions
    │   ├── features/results/      # Benchmark comparison tables
    │   └── features/overview/     # Empirical findings & platform limitations
    └── dist/                      # Pre-compiled static assets served by FastAPI
```

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
