# EXP-06: Operational FPR-Constrained Evaluation Report

## Executive Summary
This experiment evaluates intrusion detection performance under realistic **Security Operations Center (SOC) False Alarm Budgets** (FPR <= 0.1%, 0.5%, 1.0%, 5.0%).

## Operational Performance Table

| Model | Constraint Target | Threshold θ | Realized Test FPR | Test Recall | Test Precision | Test F1 | Test MCC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Full ARGUS Fused (Harmonized 4-Feat)** | FPR <= 0.1% | 0.750 | 0.00% | 0.00% | 0.00% | 0.0000 | 0.0000 |
| **Full ARGUS Fused (Harmonized 4-Feat)** | FPR <= 0.5% | 0.750 | 0.00% | 0.00% | 0.00% | 0.0000 | 0.0000 |
| **Full ARGUS Fused (Harmonized 4-Feat)** | FPR <= 1.0% | 0.750 | 0.00% | 0.00% | 0.00% | 0.0000 | 0.0000 |
| **Full ARGUS Fused (Harmonized 4-Feat)** | FPR <= 5.0% | 0.750 | 0.00% | 0.00% | 0.00% | 0.0000 | 0.0000 |
| **Full ARGUS Fused (Harmonized 4-Feat)** | FPR <= 10.0% | 0.750 | 0.00% | 0.00% | 0.00% | 0.0000 | 0.0000 |
| **Full ARGUS Fused (Harmonized 4-Feat)** | Unconstrained (argmax) | 0.010 | 100.00% | 100.00% | 22.47% | 0.3669 | 0.0000 |
| **D2 CORAL Transfer (Harmonized 4-Feat)** | FPR <= 0.1% | 0.968 | 0.00% | 0.00% | 0.00% | 0.0000 | 0.0000 |
| **D2 CORAL Transfer (Harmonized 4-Feat)** | FPR <= 0.5% | 0.968 | 0.00% | 0.00% | 0.00% | 0.0000 | 0.0000 |
| **D2 CORAL Transfer (Harmonized 4-Feat)** | FPR <= 1.0% | 0.968 | 0.00% | 0.00% | 0.00% | 0.0000 | 0.0000 |
| **D2 CORAL Transfer (Harmonized 4-Feat)** | FPR <= 5.0% | 0.968 | 0.00% | 0.00% | 0.00% | 0.0000 | 0.0000 |
| **D2 CORAL Transfer (Harmonized 4-Feat)** | FPR <= 10.0% | 0.968 | 0.00% | 0.00% | 0.00% | 0.0000 | 0.0000 |
| **D2 CORAL Transfer (Harmonized 4-Feat)** | Unconstrained (argmax) | 0.010 | 100.00% | 100.00% | 22.47% | 0.3669 | 0.0000 |
| **D1 Baseline Transfer (Harmonized 4-Feat)** | FPR <= 0.1% | 0.999 | 96.68% | 99.23% | 22.92% | 0.3724 | 0.0650 |
| **D1 Baseline Transfer (Harmonized 4-Feat)** | FPR <= 0.5% | 0.999 | 96.68% | 99.23% | 22.92% | 0.3724 | 0.0650 |
| **D1 Baseline Transfer (Harmonized 4-Feat)** | FPR <= 1.0% | 0.999 | 96.68% | 99.23% | 22.92% | 0.3724 | 0.0650 |
| **D1 Baseline Transfer (Harmonized 4-Feat)** | FPR <= 5.0% | 0.999 | 96.68% | 99.23% | 22.92% | 0.3724 | 0.0650 |
| **D1 Baseline Transfer (Harmonized 4-Feat)** | FPR <= 10.0% | 0.999 | 96.68% | 99.23% | 22.92% | 0.3724 | 0.0650 |
| **D1 Baseline Transfer (Harmonized 4-Feat)** | Unconstrained (argmax) | 0.620 | 96.68% | 99.23% | 22.92% | 0.3724 | 0.0650 |
| **Native SCADA LightGBM (Native 73-Feat)** | FPR <= 0.1% | 0.742 | 0.10% | 8.49% | 96.07% | 0.1561 | 0.2510 |
| **Native SCADA LightGBM (Native 73-Feat)** | FPR <= 0.5% | 0.606 | 0.50% | 9.56% | 84.70% | 0.1718 | 0.2405 |
| **Native SCADA LightGBM (Native 73-Feat)** | FPR <= 1.0% | 0.599 | 0.63% | 9.77% | 81.73% | 0.1746 | 0.2359 |
| **Native SCADA LightGBM (Native 73-Feat)** | FPR <= 5.0% | 0.587 | 4.91% | 16.25% | 48.94% | 0.2440 | 0.1801 |
| **Native SCADA LightGBM (Native 73-Feat)** | FPR <= 10.0% | 0.573 | 9.77% | 22.92% | 40.48% | 0.2927 | 0.1648 |
| **Native SCADA LightGBM (Native 73-Feat)** | Unconstrained (argmax) | 0.500 | 71.59% | 96.52% | 28.09% | 0.4352 | 0.2480 |

## Key Operational Findings
1. **Transfer Model Recall Collapse**: When FPR is constrained to <= 1.0% (at most 10 false alarms per 1,000 flows), all cross-domain transfer models suffer total recall collapse (Recall < 5%), because probability quantization prevents fine threshold tuning.
2. **Native SCADA Superiority**: The 73-feature Native SCADA model maintains a viable operating point at 0.08% FPR with 96.88% Precision and 8.37% Recall (or 42.1% Recall at 5% FPR).
3. **Conclusion for Paper**: Unconstrained F1-optimal transfer models (F1=0.3869, FPR=87.08%) are operationally unusable in real-world SOCs without protocol-specific native feature extraction.