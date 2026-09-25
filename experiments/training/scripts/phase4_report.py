import os
import json
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

plt.switch_backend('Agg')

def load_metrics(exp_name: str):
    metrics_file = Path(f"training/exports/{exp_name}/reports/metrics.json")
    if not metrics_file.exists():
        return None
    with open(metrics_file, "r") as f:
        return json.load(f)

def main():
    print("=== ARGUS Phase 4: Generalization Report ===")
    
    experiments = {
        "Exp1_NF_NF": "exp_nftoniotv2_nftoniotv2",
        "Exp2_CIC_CIC": "exp_ciciot2023_ciciot2023",
        "Exp3_NF_CIC": "exp_nftoniotv2_ciciot2023",
        "Exp4_CIC_NF": "exp_ciciot2023_nftoniotv2"
    }
    
    all_data = []
    
    for exp_label, exp_dir in experiments.items():
        metrics = load_metrics(exp_dir)
        if not metrics:
            print(f"[!] Warning: Metrics for {exp_label} not found. Skipping.")
            continue
            
        for model_name, m in metrics.items():
            all_data.append({
                "Experiment": exp_label,
                "Model": model_name,
                "F1": m["F1"],
                "Accuracy": m["Accuracy"],
                "ROC_AUC": m["ROC_AUC"],
                "Balanced_Accuracy": m["Balanced_Accuracy"]
            })
            
    if not all_data:
        print("[!] No experimental data found. Run Phase 3 first.")
        return
        
    df = pd.DataFrame(all_data)
    
    report_dir = Path("training/reports/generalization")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(report_dir / "generalization_metrics.csv", index=False)
    
    print("\n[*] Generalization Summary:")
    print(df.groupby(['Experiment', 'Model'])[['F1', 'Accuracy']].mean())
    
    # Analyze Performance Drop (Generalization Score)
    # Compare Exp1 (NF->NF) vs Exp3 (NF->CIC)
    try:
        nf_nf = df[df['Experiment'] == 'Exp1_NF_NF'].set_index('Model')['F1']
        nf_cic = df[df['Experiment'] == 'Exp3_NF_CIC'].set_index('Model')['F1']
        drop_nf = nf_nf - nf_cic
        
        cic_cic = df[df['Experiment'] == 'Exp2_CIC_CIC'].set_index('Model')['F1']
        cic_nf = df[df['Experiment'] == 'Exp4_CIC_NF'].set_index('Model')['F1']
        drop_cic = cic_cic - cic_nf
        
        drop_df = pd.DataFrame({
            "NF_Trained_Drop (NF->CIC)": drop_nf,
            "CIC_Trained_Drop (CIC->NF)": drop_cic
        })
        
        print("\n[*] Performance Drop (F1 Difference):")
        print(drop_df)
        drop_df.to_csv(report_dir / "performance_drop.csv")
        
        # Plot Generalization Drop
        plt.figure(figsize=(10, 6))
        drop_df.plot(kind='bar')
        plt.title("Cross-Dataset Performance Drop (Lower is Better Generalization)")
        plt.ylabel("F1 Score Drop")
        plt.tight_layout()
        plt.savefig(report_dir / "generalization_drop.png", dpi=300)
        plt.close()
        
    except Exception as e:
        print(f"[!] Could not calculate performance drop (Not all experiments completed yet).")
        
    with open(report_dir / "generalization_report.md", "w") as f:
        f.write("# ARGUS Generalization Report\n\n")
        f.write("This report evaluates how models trained on one dataset generalize to unseen datasets.\n\n")
        f.write("## All Metrics\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n\n## Overfitting / Generalization Analysis\n")
        f.write("Models with high intra-dataset F1 but massive cross-dataset drops are overfitting to dataset-specific signatures.\n")
        
    print(f"\n[*] Report saved to {report_dir}")

if __name__ == "__main__":
    main()
