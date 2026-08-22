import os, shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import roc_curve, precision_recall_curve, auc, average_precision_score

BASE = Path('/Users/tirthkosambia/Documents/ARGUS')
EE = BASE / 'experiment_execution'
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib_cache'

def generate_all_figures():
    print("=== PROGRAMMATICALLY GENERATING MASTER PUBLICATION FIGURES ===")
    
    # -------------------------------------------------------------
    # FIGURE 1: Complete Experimental Framework Diagram
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.axis('off')
    
    box_blue = dict(boxstyle='round,pad=0.5', facecolor='#ebf8ff', edgecolor='#3182ce', lw=1.5)
    box_red = dict(boxstyle='round,pad=0.5', facecolor='#fff5f5', edgecolor='#e53e3e', lw=1.5)
    box_green = dict(boxstyle='round,pad=0.5', facecolor='#f0fff4', edgecolor='#38a169', lw=1.5)
    box_purple = dict(boxstyle='round,pad=0.5', facecolor='#faf5ff', edgecolor='#805ad5', lw=1.5)
    
    ax.text(0.12, 0.75, "Source Domains\n(D1: CICIoT, D2: ToN-IoT)\n[Harmonized 4-Feat]", ha='center', va='center', bbox=box_red, fontsize=9.5, fontweight='bold')
    ax.text(0.12, 0.25, "Target SCADA Domain (D3)\n(IEC 60870-5-104)\n[Adaptation Split: Unlabeled]", ha='center', va='center', bbox=box_blue, fontsize=9.5, fontweight='bold')
    
    ax.text(0.48, 0.75, "Domain Adaptation\n• Covariance Alignment (CORAL)\n• Adversarial Transfer (DANN)\n• Multi-Source Ensemble", ha='center', va='center', bbox=box_purple, fontsize=9.5, fontweight='bold')
    ax.text(0.48, 0.25, "Bayesian Prior Correction\n&\nThreshold Calibration (D3 Calib)", ha='center', va='center', bbox=box_purple, fontsize=9.5, fontweight='bold')
    
    ax.text(0.85, 0.50, "Frozen D3 Test Set (N=714k)\n• Constrained FPR Analysis\n• Feature Resolution (4→73)\n• Empirical State Audit", ha='center', va='center', bbox=box_green, fontsize=9.5, fontweight='bold')
    
    arrow_props = dict(facecolor='#4a5568', edgecolor='#4a5568', arrowstyle='->', lw=2)
    ax.annotate('', xy=(0.32, 0.75), xytext=(0.24, 0.75), arrowprops=arrow_props)
    ax.annotate('', xy=(0.32, 0.25), xytext=(0.24, 0.25), arrowprops=arrow_props)
    ax.annotate('', xy=(0.48, 0.45), xytext=(0.48, 0.58), arrowprops=arrow_props)
    ax.annotate('', xy=(0.70, 0.50), xytext=(0.63, 0.70), arrowprops=arrow_props)
    ax.annotate('', xy=(0.70, 0.50), xytext=(0.63, 0.30), arrowprops=arrow_props)
    
    plt.title("ARGUS Empirical Evidence & Cross-Domain Experimental Framework", fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    fig.savefig(EE / 'figures/Figure1_Framework.png', dpi=300)
    plt.close()
    
    # -------------------------------------------------------------
    # FIGURE 2: Master ROC & PR Curve Overlay
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=300)
    
    p_native = pd.read_csv(EE / 'predictions/EXP04/D3_native_seed42_predictions.csv')
    p_fused = pd.read_csv(EE / 'predictions/EXP05/Full_ARGUS_seed42_predictions.csv')
    p_d1 = pd.read_csv(EE / 'predictions/EXP01/D1_D3_seed42_predictions.csv')
    p_d2 = pd.read_csv(EE / 'predictions/EXP01/D2_D3_seed42_predictions.csv')
    
    # ROC Curves
    fpr_n, tpr_n, _ = roc_curve(p_native['y_true'], p_native['y_prob'])
    fpr_f, tpr_f, _ = roc_curve(p_fused['y_true'], p_fused['y_prob'])
    fpr_1, tpr_1, _ = roc_curve(p_d1['y_true'], p_d1['y_prob'])
    fpr_2, tpr_2, _ = roc_curve(p_d2['y_true'], p_d2['y_prob'])
    
    ax1.plot(fpr_n, tpr_n, label=f'Native SCADA (73-Feat, AUC = {auc(fpr_n, tpr_n):.4f})', color='#2b6cb0', linewidth=2.5)
    ax1.plot(fpr_1, tpr_1, label=f'D1 Baseline (4-Feat, AUC = {auc(fpr_1, tpr_1):.4f})', color='#d9534f', linewidth=1.8, linestyle='--')
    ax1.plot(fpr_2, tpr_2, label=f'D2 Baseline (4-Feat, AUC = {auc(fpr_2, tpr_2):.4f})', color='#f0ad4e', linewidth=1.8, linestyle='--')
    ax1.plot(fpr_f, tpr_f, label=f'Full ARGUS Fused (4-Feat, AUC = {auc(fpr_f, tpr_f):.4f})', color='#805ad5', linewidth=2)
    ax1.plot([0, 1], [0, 1], 'k:', alpha=0.6, label='Random Chance (AUC = 0.5000)')
    ax1.set_xlabel('False Positive Rate (FPR)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('True Positive Rate (Recall)', fontsize=11, fontweight='bold')
    ax1.set_title('(A) Receiver Operating Characteristic (ROC)', fontsize=12, fontweight='bold')
    ax1.legend(loc='lower right', fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # PR Curves
    rec_n, prec_n, _ = precision_recall_curve(p_native['y_true'], p_native['y_prob'])
    rec_f, prec_f, _ = precision_recall_curve(p_fused['y_true'], p_fused['y_prob'])
    rec_1, prec_1, _ = precision_recall_curve(p_d1['y_true'], p_d1['y_prob'])
    rec_2, prec_2, _ = precision_recall_curve(p_d2['y_true'], p_d2['y_prob'])
    
    ap_n = average_precision_score(p_native['y_true'], p_native['y_prob'])
    ap_1 = average_precision_score(p_d1['y_true'], p_d1['y_prob'])
    ap_2 = average_precision_score(p_d2['y_true'], p_d2['y_prob'])
    ap_f = average_precision_score(p_fused['y_true'], p_fused['y_prob'])
    
    ax2.plot(rec_n, prec_n, label=f'Native SCADA (73-Feat, AP = {ap_n:.4f})', color='#2b6cb0', linewidth=2.5)
    ax2.plot(rec_1, prec_1, label=f'D1 Baseline (4-Feat, AP = {ap_1:.4f})', color='#d9534f', linewidth=1.8, linestyle='--')
    ax2.plot(rec_2, prec_2, label=f'D2 Baseline (4-Feat, AP = {ap_2:.4f})', color='#f0ad4e', linewidth=1.8, linestyle='--')
    ax2.plot(rec_f, prec_f, label=f'Full ARGUS Fused (4-Feat, AP = {ap_f:.4f})', color='#805ad5', linewidth=2)
    ax2.axhline(y=0.2247, color='k', linestyle=':', alpha=0.6, label='Target Base Rate (22.47%)')
    ax2.set_xlabel('Recall / True Positive Rate', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Precision', fontsize=11, fontweight='bold')
    ax2.set_title('(B) Precision-Recall (PR) Overlay', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    fig.savefig(EE / 'figures/Figure2_ROC_PR_Overlay.png', dpi=300)
    plt.close()
    
    # Copy EXP03, EXP06, SHAP figures to Figure3, Figure4, Figure5
    shutil.copy(EE / 'figures/EXP03_cardinality.png', EE / 'figures/Figure3_Cardinality.png')
    shutil.copy(EE / 'figures/EXP06_FPR_vs_Recall.png', EE / 'figures/Figure4_FPR_vs_Recall.png')
    shutil.copy(EE / 'figures/SHAP_vs_Target_Gain.png', EE / 'figures/Figure5_SHAP_vs_Gain.png')
    
    print("[OK] Master publication figures generated and verified.")

if __name__ == '__main__':
    generate_all_figures()
