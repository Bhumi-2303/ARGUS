import json
import os
import pandas as pd
import numpy as np

# Create output directories
base_dir = "results/ARGUS_POSTER_DATA_PACKAGE"
os.makedirs(f"{base_dir}/graphs", exist_ok=True)
os.makedirs(f"{base_dir}/figures/confusion_matrices", exist_ok=True)

# 1. Dataset Statistics
dataset_stats = [
    {"dataset": "CICIoT2023", "samples": 6668822, "features": 4, "classes": 2, "domain": "D1"},
    {"dataset": "NF-ToN-IoT-v2", "samples": 13135881, "features": 4, "classes": 2, "domain": "D2"},
    {"dataset": "IEC 60870-5-104 (SCADA)", "samples": 3572265, "features": 70, "classes": 2, "domain": "D3"}
]
df_ds = pd.DataFrame(dataset_stats)
df_ds.to_csv(f"{base_dir}/dataset_statistics.csv", index=False)


# 2. Feature Summary
df_audit = pd.read_csv("phase4_results/feature_resolution/feature_audit.csv")
df_card = pd.read_csv("phase4_results/feature_resolution/representation_cardinality.csv")
df_shift = pd.read_csv("phase3_results/domain_shift/domain_shift_statistics.csv")

feature_summary = []
for idx, row in df_audit.iterrows():
    if "YES (ARGUS-4 Baseline)" in str(row["Selected"]):
        feature_summary.append({
            "feature": row["Candidate"],
            "status": "Selected (ARGUS-4)",
            "description": row["Formula"],
            "units": row["Units"]
        })
for idx, row in df_card.iterrows():
    feature_summary.append({
        "feature": row["Representation"],
        "status": "Representation Setup",
        "description": f"{row['Features']} features, {row['Unique Tuples']} unique tuples",
        "units": "-"
    })

pd.DataFrame(feature_summary).to_csv(f"{base_dir}/feature_summary.csv", index=False)

# 3. Poster Results & Confusion Matrices
poster_results = []
cross_domain_f1 = []
cross_domain_mcc = []
fpr_fnr = []
domain_transfer = []

with open("phase4_results/metrics/all_results.json") as f:
    phase4 = json.load(f)

for exp_id, data in phase4.items():
    if exp_id == "table_b" or exp_id == "table_c" or type(data) is not dict:
        continue
    config = data.get("Config", {})
    source_domain = config.get("Source", "UNKNOWN")
    method = config.get("Method", "UNKNOWN")
    model = f"LightGBM ({method})"
    
    # Try Calibrated F1 first, else Uncalibrated
    if "Calibrated" in data and "F1" in data["Calibrated"]:
        metrics = data["Calibrated"]["F1"]
    else:
        metrics = data.get("Uncalibrated", {})
        
    if not metrics:
        continue
        
    acc = metrics.get("Accuracy", "[DATA NOT AVAILABLE]")
    prec = metrics.get("Precision", "[DATA NOT AVAILABLE]")
    rec = metrics.get("Recall", "[DATA NOT AVAILABLE]")
    f1 = metrics.get("F1", "[DATA NOT AVAILABLE]")
    mcc = metrics.get("MCC", "[DATA NOT AVAILABLE]")
    fpr = metrics.get("FPR", "[DATA NOT AVAILABLE]")
    fnr = metrics.get("FNR", "[DATA NOT AVAILABLE]")
    roc_auc = metrics.get("ROC_AUC", "[DATA NOT AVAILABLE]")
    pr_auc = metrics.get("PR_AUC", "[DATA NOT AVAILABLE]")
    
    tp = metrics.get("TP")
    tn = metrics.get("TN")
    fp = metrics.get("FP")
    fn = metrics.get("FN")
    
    # Calculate confusion matrix if exist
    if all(x is not None for x in [tp, tn, fp, fn]):
        cm_df = pd.DataFrame({
            "Predicted_Benign": [tn, fn],
            "Predicted_Attack": [fp, tp]
        }, index=["Actual_Benign", "Actual_Attack"])
        cm_df.to_csv(f"{base_dir}/figures/confusion_matrices/{exp_id}_cm.csv")
        
    poster_results.append({
        "experiment_id": exp_id,
        "source_domain": source_domain,
        "target_domain": "D3",
        "model": model,
        "samples": 714453, # Test size for D3
        "classes": 2,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "mcc": mcc,
        "fpr": fpr,
        "fnr": fnr,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "training_time": "[DATA NOT AVAILABLE]",
        "inference_time": "[DATA NOT AVAILABLE]",
        "source_file": "phase4_results/metrics/all_results.json"
    })
    
    cross_domain_f1.append({
        "source_domain": source_domain,
        "target_domain": "D3",
        "model": model,
        "f1": f1
    })
    cross_domain_mcc.append({
        "source_domain": source_domain,
        "target_domain": "D3",
        "model": model,
        "mcc": mcc
    })
    fpr_fnr.append({
        "source_domain": source_domain,
        "target_domain": "D3",
        "model": model,
        "fpr": fpr,
        "fnr": fnr
    })
    domain_transfer.append({
        "source_domain": source_domain,
        "target_domain": "D3",
        "model": model,
        "metric": "F1",
        "value": f1
    })

# Add Phase 3 models (DANN)
with open("phase3_results/metrics_validation_report.json") as f:
    phase3 = json.load(f)

for exp in phase3.get("table_a", []):
    if "DANN" in exp["Experiment"]:
        exp_id = exp["Experiment"]
        source_domain = "D1" if "D1" in exp_id else "D2"
        model = "DANN"
        
        poster_results.append({
            "experiment_id": exp_id,
            "source_domain": source_domain,
            "target_domain": "D3",
            "model": model,
            "samples": 714453,
            "classes": 2,
            "accuracy": exp.get("Accuracy"),
            "precision": exp.get("Precision"),
            "recall": exp.get("Recall"),
            "f1": exp.get("F1"),
            "mcc": exp.get("MCC"),
            "fpr": exp.get("FPR"),
            "fnr": exp.get("FNR"),
            "roc_auc": exp.get("ROC_AUC"),
            "pr_auc": exp.get("PR_AUC"),
            "training_time": "[DATA NOT AVAILABLE]",
            "inference_time": "[DATA NOT AVAILABLE]",
            "source_file": "phase3_results/metrics_validation_report.json"
        })
        cross_domain_f1.append({
            "source_domain": source_domain,
            "target_domain": "D3",
            "model": model,
            "f1": exp.get("F1")
        })
        cross_domain_mcc.append({
            "source_domain": source_domain,
            "target_domain": "D3",
            "model": model,
            "mcc": exp.get("MCC")
        })
        fpr_fnr.append({
            "source_domain": source_domain,
            "target_domain": "D3",
            "model": model,
            "fpr": exp.get("FPR"),
            "fnr": exp.get("FNR")
        })
        domain_transfer.append({
            "source_domain": source_domain,
            "target_domain": "D3",
            "model": model,
            "metric": "F1",
            "value": exp.get("F1")
        })

# FTT models
ftt_df = pd.read_csv("experiment_execution/neural_robustness/tables/N1_LightGBM_vs_FTTransformer.csv")
for idx, row in ftt_df.iterrows():
    if row["model_family"] == "FT-Transformer Neural":
        exp_id = f"FTT_{row['condition']}"
        f1_val = float(str(row["f1_mean"]).split(" ")[0])
        mcc_val = float(str(row["mcc_mean"]).split(" ")[0])
        fpr_val = float(str(row["fpr_mean"]).split(" ")[0])
        fnr_val = float(str(row["fnr_mean"]).split(" ")[0])
        model = "FT-Transformer Neural"
        poster_results.append({
            "experiment_id": exp_id,
            "source_domain": "D1",
            "target_domain": "D3",
            "model": model,
            "samples": 714453,
            "classes": 2,
            "accuracy": float(str(row["accuracy_mean"]).split(" ")[0]),
            "precision": float(str(row["precision_mean"]).split(" ")[0]),
            "recall": float(str(row["recall_mean"]).split(" ")[0]),
            "f1": f1_val,
            "mcc": mcc_val,
            "fpr": fpr_val,
            "fnr": fnr_val,
            "roc_auc": float(str(row["roc_auc_mean"]).split(" ")[0]),
            "pr_auc": float(str(row["pr_auc_mean"]).split(" ")[0]),
            "training_time": "[DATA NOT AVAILABLE]",
            "inference_time": "[DATA NOT AVAILABLE]",
            "source_file": "experiment_execution/neural_robustness/tables/N1_LightGBM_vs_FTTransformer.csv"
        })
        cross_domain_f1.append({
            "source_domain": "D1",
            "target_domain": "D3",
            "model": model,
            "f1": f1_val
        })
        cross_domain_mcc.append({
            "source_domain": "D1",
            "target_domain": "D3",
            "model": model,
            "mcc": mcc_val
        })
        fpr_fnr.append({
            "source_domain": "D1",
            "target_domain": "D3",
            "model": model,
            "fpr": fpr_val,
            "fnr": fnr_val
        })
        domain_transfer.append({
            "source_domain": "D1",
            "target_domain": "D3",
            "model": model,
            "metric": "F1",
            "value": f1_val
        })

pd.DataFrame(poster_results).to_csv(f"{base_dir}/poster_results.csv", index=False)
pd.DataFrame(cross_domain_f1).to_csv(f"{base_dir}/graphs/01_cross_domain_f1.csv", index=False)
pd.DataFrame(cross_domain_mcc).to_csv(f"{base_dir}/graphs/02_cross_domain_mcc.csv", index=False)
pd.DataFrame(fpr_fnr).to_csv(f"{base_dir}/graphs/03_fpr_fnr.csv", index=False)
pd.DataFrame(domain_transfer).to_csv(f"{base_dir}/graphs/05_domain_transfer.csv", index=False)

# 4. Runtime
runtime_df = pd.read_csv("phase4_results/feature_resolution/runtime_statistics.csv")
runtime_data = []
for idx, row in runtime_df.iterrows():
    runtime_data.append({
        "model": row["Unnamed: 0"], # Representation
        "experiment_id": "All",
        "training_time": row["Training Time (s)"],
        "inference_time": row["Inference Time (s)"]
    })
pd.DataFrame(runtime_data).to_csv(f"{base_dir}/graphs/04_runtime.csv", index=False)

