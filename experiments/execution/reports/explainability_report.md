# Explainability & Feature Importance Disconnect Report

## Executive Summary
This analysis contrasts the feature importance discovered by SHAP on source IoT traffic against the actual predictive feature gain on target IEC 60870-5-104 SCADA traffic.

## Key Findings
1. **The Disconnect**: Source SHAP ranks `log_pkt_max` as the #1 predictive feature (37.48% importance) because IoT DDoS floods are characterized by large packet sizes. However, in SCADA traffic, polling messages have nearly identical maximum packet sizes, making this feature ineffective for target detection.
2. **What Actually Separates SCADA Traffic**: Target SCADA traffic is separated primarily by **TCP Header Lengths**, **Window Parameters (`Init Fwd Win Byts`)**, and **Inter-Arrival Times (`Flow IAT Mean`)**—all of which were discarded during 4-feature harmonization.
3. **Conclusion for Paper**: Explainability techniques (SHAP) explain how tree models make decisions in the *source* domain, but cannot be treated as causal invariants for unseen industrial protocols.