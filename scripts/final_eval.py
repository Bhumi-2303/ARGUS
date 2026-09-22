import os
import json
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import (
    matthews_corrcoef, balanced_accuracy_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
import warnings
warnings.filterwarnings("ignore")

DATA_DIR = "/home/bhumi/Downloads/ARGUS_Cross_Domain_Results/argus_coral_data"
FEATURES = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']
TARGET = 'label'
WINDOW_SIZE = 50000

def load_models():
    m_src = xgb.XGBClassifier()
    m_src.load_model("artifacts/models/xgb_source.json")
    m_adapt = xgb.XGBClassifier()
    m_adapt.load_model("artifacts/models/xgb_adapted.json")
    return m_src, m_adapt

def calculate_metrics(y_true, y_prob, y_pred, prior=None):
    if len(y_true) == 0:
        return {}
    mcc = matthews_corrcoef(y_true, y_pred)
    bacc = balanced_accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    try:
        roc_auc = roc_auc_score(y_true, y_prob)
        pr_auc = average_precision_score(y_true, y_prob)
    except:
        roc_auc, pr_auc = 0.5, prior if prior is not None else 0.5
    
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    if cm.size == 4:
        tn, fp, fn, tp = cm.ravel()
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    else:
        specificity = 0
        
    return {
        "mcc": mcc, "bacc": bacc, "f1": f1,
        "roc_auc": roc_auc, "pr_auc": pr_auc, "specificity": specificity
    }

def bootstrap_ci(y_true, y_prob, y_pred, prior, n_resamples=10):
    n = len(y_true)
    metrics_list = {k: [] for k in ["mcc", "bacc", "f1", "roc_auc", "pr_auc", "specificity"]}
    
    # Pre-calculate overall
    overall = calculate_metrics(y_true, y_prob, y_pred, prior)
    
    for seed in range(n_resamples):
        np.random.seed(seed)
        idx = np.random.randint(0, n, n)
        res = calculate_metrics(y_true[idx], y_prob[idx], y_pred[idx], prior)
        for k, v in res.items():
            metrics_list[k].append(v)
            
    ci_results = {}
    for k, vals in metrics_list.items():
        v_arr = np.array(vals)
        v_arr = v_arr[~np.isnan(v_arr)]
        if len(v_arr) == 0:
            ci_results[k] = "0.000 [0.000, 0.000]"
        else:
            lower = np.percentile(v_arr, 2.5)
            upper = np.percentile(v_arr, 97.5)
            mean_val = overall.get(k, 0.0)
            ci_results[k] = f"{mean_val:.3f} [{lower:.3f}, {upper:.3f}]"
            
    return ci_results, overall

def check_drift(features, ref_mean, ref_std, threshold=0.2):
    cur_mean = np.mean(features, axis=0)
    shift = np.abs(cur_mean - ref_mean) / ref_std
    return np.max(shift) > threshold

def evaluate_scenario(name, df, m_src, m_adapt, params, ref_mean, ref_std):
    print(f"\n--- Evaluating {name} ---")
    y_true = df[TARGET].values
    features = df[FEATURES].values
    
    p_src = m_src.predict_proba(features)[:, 1]
    p_adapt = m_adapt.predict_proba(features)[:, 1]
    
    th_A = params["source_threshold"]
    th_B = params["adapted_threshold"]
    w = params["blend_w"]
    th_D = params["blend_threshold"]
    prior = params["prior"]
    
    # Candidate A
    y_pred_A = (p_src >= th_A).astype(int)
    ci_A, _ = bootstrap_ci(y_true, p_src, y_pred_A, prior)
    
    # Candidate B
    y_pred_B = (p_adapt >= th_B).astype(int)
    ci_B, _ = bootstrap_ci(y_true, p_adapt, y_pred_B, prior)
    
    # Candidate C (Drift-gated)
    p_C = np.zeros_like(p_src)
    y_pred_C = np.zeros_like(y_true)
    
    for i in range(0, len(y_true), WINDOW_SIZE):
        end = min(i + WINDOW_SIZE, len(y_true))
        feat_window = features[i:end]
        is_drift = check_drift(feat_window, ref_mean, ref_std)
        if is_drift:
            p_C[i:end] = p_adapt[i:end]
            y_pred_C[i:end] = (p_adapt[i:end] >= th_B).astype(int)
        else:
            p_C[i:end] = p_src[i:end]
            y_pred_C[i:end] = (p_src[i:end] >= th_A).astype(int)
            
    ci_C, _ = bootstrap_ci(y_true, p_C, y_pred_C, prior)
    
    # Candidate D (Score Average)
    p_D = w * p_src + (1 - w) * p_adapt
    y_pred_D = (p_D >= th_D).astype(int)
    ci_D, _ = bootstrap_ci(y_true, p_D, y_pred_D, prior)
    
    # Candidate E (Baselines)
    # E1: Always Attack
    y_pred_E1 = np.ones_like(y_true)
    ci_E1, _ = bootstrap_ci(y_true, p_src, y_pred_E1, prior)  # prob doesn't matter for E1 metrics except ROC/PR
    
    # E2: Prevalence random
    np.random.seed(42)
    y_pred_E2 = (np.random.rand(len(y_true)) < prior).astype(int)
    ci_E2, _ = bootstrap_ci(y_true, p_src, y_pred_E2, prior)
    
    results = {
        "A": ci_A,
        "B": ci_B,
        "C": ci_C,
        "D": ci_D,
        "E_always": ci_E1,
        "E_random": ci_E2
    }
    
    for cand, cimet in results.items():
        print(f"Candidate {cand}: MCC={cimet['mcc']}")
        
    return results

def log_test_access():
    with open("TEST_ACCESS.log", "w") as f:
        f.write("TEST_ACCESS.log\n")
        f.write("Test datasets accessed by scripts/final_eval.py on Day 4:\n")
        f.write(f"- {DATA_DIR}/nfton_test_features.csv\n")
        f.write(f"- {DATA_DIR}/ciciot_test_features.csv\n")
        f.write("- Mixed stream generated dynamically from both.\n")

def main():
    with open("artifacts/day4/fusion.json", "r") as f:
        params = json.load(f)
        
    m_src, m_adapt = load_models()
    
    # Get reference stats for drift detector (from CICIoT Train, the source)
    print("Computing reference stats from CICIoT Train...")
    df_ref = pd.read_csv(f"{DATA_DIR}/ciciot_train_features.csv", nrows=100000)
    ref_mean = np.mean(df_ref[FEATURES].values, axis=0)
    ref_std = np.std(df_ref[FEATURES].values, axis=0) + 1e-8
    del df_ref
    
    print("Loading NF-ToN Test...")
    df_nfton = pd.read_csv(f"{DATA_DIR}/nfton_test_features.csv")
    print("Loading CICIoT Test...")
    df_ciciot = pd.read_csv(f"{DATA_DIR}/ciciot_test_features.csv")
    
    # Mixed stream
    print("Creating mixed stream...")
    mixed_chunks = []
    i, j = 0, 0
    use_ciciot = True
    while i < len(df_ciciot) or j < len(df_nfton):
        if use_ciciot and i < len(df_ciciot):
            end = min(i + WINDOW_SIZE, len(df_ciciot))
            mixed_chunks.append(df_ciciot.iloc[i:end])
            i = end
        elif not use_ciciot and j < len(df_nfton):
            end = min(j + WINDOW_SIZE, len(df_nfton))
            mixed_chunks.append(df_nfton.iloc[j:end])
            j = end
        elif i >= len(df_ciciot):
            use_ciciot = False
            continue
        elif j >= len(df_nfton):
            use_ciciot = True
            continue
        use_ciciot = not use_ciciot
        
    df_mixed = pd.concat(mixed_chunks, ignore_index=True)
    
    log_test_access()
    
    res_target = evaluate_scenario("NF-ToN Test (Target)", df_nfton, m_src, m_adapt, params, ref_mean, ref_std)
    res_source = evaluate_scenario("CICIoT Test (Source)", df_ciciot, m_src, m_adapt, params, ref_mean, ref_std)
    res_mixed = evaluate_scenario("Mixed Stream", df_mixed, m_src, m_adapt, params, ref_mean, ref_std)
    
    # Save results to a json file to be formatted into markdown
    with open("artifacts/day4/results.json", "w") as f:
        json.dump({
            "target": res_target,
            "source": res_source,
            "mixed": res_mixed,
            "winner": params["winner"],
            "cal_mcc": params["calibration_mcc"]
        }, f, indent=4)
        
    print("Finished evaluating. Saved to artifacts/day4/results.json")

if __name__ == "__main__":
    main()
