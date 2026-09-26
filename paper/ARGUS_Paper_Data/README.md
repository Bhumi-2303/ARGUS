# ARGUS Paper Data Export

This directory contains the exact deliverables and datasets requested for the ARGUS paper writing, organized into specific folders matching your request items:

1. **1_DANN_Predictions/**: Contains the raw D1→D2 predictions for the DANN model, properly formatted with `sample_index`, `true_label`, and `predicted_probability`.
2. **2_REP01_Deliverables/**: Contains the complete REP-01 experiment footprint, including the final report (`REP01_FINAL_REPORT.md`), the leakage audit (`REP01_LEAKAGE_AUDIT.md`), and representation comparisons. 
3. **3_Entropy_Computation/**: Contains `entropy_results.txt`, which proves the 714,453 test flows for IEC 104 collapse to 1,704 unique tuples (2.04 bits entropy).
4. **4_Baseline_Predictions/**: Contains the raw predictions for the four D1↔D2 baselines (Source-only, Global CORAL, Diagnostic Class-aware CORAL, and Clean Class-aware CORAL).
5. **5_SHAP_Values/**: Contains the SHAP attribution values for the Clean Class-aware CORAL model before and after adaptation.

