# ARGUS ACTION PLAN

### MUST FIX (Before any new experiments)
1. **Data Leakage**: Implement exact strict deduplication across source and target domains. Target data must be completely blind.
2. **Result Integrity**: Delete the fabricated `ARGUS_RESULTS_README.txt` and all legacy output files to prevent accidental reuse.
3. **Pipeline Truth**: Ensure that any published metric is derived directly from a version-controlled script (e.g., via Make/DVC).

### RECOMMENDED EXPERIMENTAL ROADMAP
1. **Experiment 0: Strict Isolation**: Re-split datasets guaranteeing 0% feature-vector overlap.
2. **Experiment 1: Within-Domain**: Train XGBoost strictly within CICIoT2023.
3. **Experiment 2: True Zero-Shot**: Evaluate CICIoT2023 model on NF-ToN-IoT *without any calibration*.
4. **Experiment 3: Agent Integration**: Feed predictions into `decision_support` agent.
