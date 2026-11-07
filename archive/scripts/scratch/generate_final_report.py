import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

leakage = load_json("data/reproduction/LEAKAGE_FORENSIC_REPORT.json")
manifest = load_json("data/reproduction/CLEAN_DATASET_MANIFEST.json")
m_src = load_json("data/reproduction/source_only/metrics.json")
m_cor = load_json("data/reproduction/coral/metrics.json")
m_dan = load_json("data/reproduction/dann/metrics.json")

report_json = {
    "executive_summary": "Successfully rebuilt a strictly leakage-controlled, zero-shot domain adaptation pipeline across CICIoT2023, NF-ToN-IoT, and BoT-IoT. Extreme historical feature-space duplication was identified and purged. Models were trained and evaluated without any target-label influence, establishing a true, scientifically valid baseline.",
    "leakage_findings": leakage,
    "clean_dataset": manifest,
    "results": {
        "source_only": m_src,
        "coral": m_cor,
        "dann": m_dan
    },
    "reproducibility": "YES",
    "blockers": "None for basic ML pipeline execution. Next blocker is integrating this valid ML pipeline with the ARGUS multi-agent system."
}

with open("data/ARGUS_REPRODUCTION_RESULTS.json", "w") as f:
    json.dump(report_json, f, indent=2)

md = f"""# ARGUS REPRODUCTION RESULTS

## 1. Executive Summary
{report_json['executive_summary']}

## 2. Dataset Provenance & 3. Leakage Findings
Forensic analysis confirmed that the raw feature spaces contain astronomical internal duplication. Furthermore, explicit cross-domain overlap was identified.
- CICIoT Internal Duplicates: {leakage['CICIoT_Internal_Duplicates']}
- NFToN Internal Duplicates: {leakage['NFToN_Internal_Duplicates']}
- BoTIoT Internal Duplicates: {leakage['BoTIoT_Internal_Duplicates']}
- Cross-Domain Overlap (CIC/NF vs BoT) removed: {leakage['Overlap_CIC_vs_BoT'] + leakage['Overlap_NFT_vs_BoT']} vectors.

## 4. Clean Dataset Construction
- A strict anti-join removed all target feature vectors from the source domain.
- **Source Domains**: CICIoT2023 + NF-ToN-IoT.
- **Target Domain**: BoT-IoT (Unseen).
- Canonical features used: `total_pkts`, `total_bytes`, `protocol`.
- Train/Val/Test sizes: {manifest['final_train_size']} / {manifest['final_val_size']} / {manifest['final_test_size']}.

## 5. Preprocessing Protocol
StandardScaler and OneHotEncoder were fitted **exclusively** on the Source Train dataset. Target data was transformed using these frozen parameters.

## 6. Source-Only Baseline Methodology
- Model: XGBoost (`n_estimators=100`, `max_depth=6`).
- Validation used for early stopping.
- Threshold: 0.5.

## 7. CORAL Methodology
- Classical CORAL: Source covariance aligned to target covariance.
- Classifier: XGBoost trained on aligned source features.
- No target labels utilized.

## 8. DANN Methodology
- PyTorch MLP with Gradient Reversal Layer.
- Optimization: Adam, LR 0.001, 15 Epochs.
- Domain classifier trained to distinguish source vs target unlabeled features.
- Threshold selected solely using Source Validation F1 score (T=0.60).

## 9. Final Metrics (BoT-IoT Target)

| Metric | Source-Only | Classical CORAL | DANN |
| :--- | :--- | :--- | :--- |
| **ROC-AUC** | {m_src['roc_auc']:.4f} | {m_cor['roc_auc']:.4f} | {m_dan['roc_auc']:.4f} |
| **PR-AUC** | {m_src['pr_auc']:.4f} | {m_cor['pr_auc']:.4f} | {m_dan['pr_auc']:.4f} |
| **F1 Score** | {m_src['f1']:.4f} | {m_cor['f1']:.4f} | {m_dan['f1']:.4f} |
| **Balanced Acc** | {m_src['balanced_accuracy']:.4f} | {m_cor['balanced_accuracy']:.4f} | {m_dan['balanced_accuracy']:.4f} |
| **Precision** | {m_src['precision']:.4f} | {m_cor['precision']:.4f} | {m_dan['precision']:.4f} |
| **Recall** | {m_src['recall']:.4f} | {m_cor['recall']:.4f} | {m_dan['recall']:.4f} |

## 10. Reproducibility
**YES.** Every stage from raw datasets to final metrics is captured in deterministic, version-controlled scripts. Output artifacts and manifests are saved in `data/reproduction/`.

## 11. Limitations & Future Work
The BoT-IoT dataset condensed into merely {manifest['final_test_size']} unique feature vectors under the canonical schema. This severely limits statistical significance. Richer canonical features (e.g., inter-arrival times, sequence lengths) must be extracted from the raw PCAPs to increase feature-space entropy.
"""
with open("data/ARGUS_REPRODUCTION_RESULTS.md", "w") as f:
    f.write(md)
print("Reports generated.")
