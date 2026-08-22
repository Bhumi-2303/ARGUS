# ARGUS Neural Robustness — Stage 1 Artifact Inventory

**Audit Date**: August 22, 2026  
**Mode**: Read-Only / No-Retrain Verification  
**Evaluation Target Partition**: Frozen IEC 60870-5-104 Test Partition ($N = 714,453$ records, $\pi_{target} = 22.47\%$)

---

## 1. Comprehensive Experiment Artifact Matrix

| Experiment | Seed | Checkpoint | Prediction | Metrics | Training Log | Figure | Status |
|---|---:|---|---|---|---|---|---|
| **N1 FT-Transformer D1→D3** | 42 | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| **N1 FT-Transformer D1→D3** | 123 | COMPLETE | MISSING (OOM Prevention) | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| **N1 FT-Transformer D1→D3** | 456 | COMPLETE | MISSING (OOM Prevention) | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| **N1 FT-Transformer D1→D3** | 789 | COMPLETE | MISSING (OOM Prevention) | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| **N1 FT-Transformer D1→D3** | 1011 | COMPLETE | MISSING (OOM Prevention) | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| **N2 FT-Transformer D2→D3** | 42 | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| **N2 FT-Transformer D2→D3** | 123 | COMPLETE | MISSING (OOM Prevention) | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| **N2 FT-Transformer D2→D3** | 456 | COMPLETE | MISSING (OOM Prevention) | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| **N2 FT-Transformer D2→D3** | 789 | COMPLETE | MISSING (OOM Prevention) | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| **N2 FT-Transformer D2→D3** | 1011 | COMPLETE | MISSING (OOM Prevention) | COMPLETE | COMPLETE | COMPLETE | COMPLETE |
| **N3 FT-Transformer Native SCADA** | 42 | COMPLETE | COMPLETE | COMPLETE (Validated) | COMPLETE | MISSING | COMPLETE |
| **N3 FT-Transformer Native SCADA** | 123 | COMPLETE | MISSING | MISSING | MISSING | MISSING | PARTIAL |
| **N3 FT-Transformer Native SCADA** | 456 | MISSING | MISSING | MISSING | MISSING | MISSING | NOT_STARTED |
| **N3 FT-Transformer Native SCADA** | 789 | MISSING | MISSING | MISSING | MISSING | MISSING | NOT_STARTED |
| **N3 FT-Transformer Native SCADA** | 1011 | MISSING | MISSING | MISSING | MISSING | MISSING | NOT_STARTED |

---

## 2. Artifact Detail & Integrity Verification

### 2.1 Model Checkpoints (`checkpoints/`)
- All 10 model checkpoints for N1 ($D1 \rightarrow D3$) and N2 ($D2 \rightarrow D3$) are present, loadable via PyTorch, and occupy 79 KB each in float32.
- N3 Native SCADA checkpoints exist for Seed 42 (95 KB) and Seed 123 (95 KB).

### 2.2 Preserved Raw Predictions (`predictions/`)
- `predictions/NR01/D1_D3_seed42_predictions.csv`: 714,453 test records (columns: `y_true`, `y_prob`).
- `predictions/NR01/D2_D3_seed42_predictions.csv`: 714,453 test records (columns: `y_true`, `y_prob`).
- `predictions/NR02/D3_native_seed42_predictions.csv`: 714,453 test records (columns: `y_true`, `y_prob`).
- *Note on Multi-Seed Predictions*: Per memory-safety guidelines, only representative Seed-42 test predictions were serialized to disk to prevent RAM/disk bloat. Multi-seed scalar metrics are recorded directly in `metrics/`.

### 2.3 Preserved Training Logs (`training_logs/`)
- N1 logs: 5 seeds (3 epochs each with early stopping on validation).
- N2 logs: 5 seeds (3-4 epochs each with early stopping).
- N3 logs: Seed 42 (10 epochs).

### 2.4 Generated Figures (300 DPI Publication-Ready)
- `figures/N1_ROC.png` & `figures/N1_ROC.csv`
- `figures/N1_PR.png` & `figures/N1_PR.csv`
- `figures/N1_confusion_matrix.png`
- `figures/N1_training_curve.png`
- `figures/N2_ROC.png` & `figures/N2_ROC.csv`
- `figures/N2_PR.png` & `figures/N2_PR.csv`
- `figures/N2_confusion_matrix.png`
- `figures/N2_training_curve.png`
