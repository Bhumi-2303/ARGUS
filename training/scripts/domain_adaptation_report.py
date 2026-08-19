#!/usr/bin/env python3
"""
ARGUS Domain Adaptation Report Generator.

Generates paper-ready visualizations and summary reports from domain
adaptation experiment results.

Outputs:
  - Comparison summary table (markdown + LaTeX)
  - Generalization drop bar chart
  - Domain AUC progression line chart
  - t-SNE visualization of feature representations
  - Statistical significance tests
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


def generate_report(
    exp1_results: Optional[Dict],
    exp2_results: Optional[Dict],
    exp3_results: Optional[Dict],
    comparison_df: Optional[pd.DataFrame],
    source_name: str,
    target_name: str,
    dirs: Dict[str, Path],
) -> None:
    """Generate all report outputs from experiment results."""
    print("[*] Generating domain adaptation report...")

    figures_dir = dirs["figures"]
    report_dir = dirs["exp4_comparison"]

    # 1. Comparison bar chart
    if comparison_df is not None and not comparison_df.empty:
        _plot_comparison_chart(comparison_df, figures_dir, source_name, target_name)

    # 2. Domain AUC comparison
    _plot_domain_auc_comparison(exp1_results, exp2_results, exp3_results, figures_dir)

    # 3. DANN training curves
    dann_history_path = dirs["exp3_dann"] / "training_history.json"
    if dann_history_path.exists():
        _plot_dann_training_curves(dann_history_path, figures_dir)

    # 4. t-SNE visualization
    source_feat_path = dirs["exp3_dann"] / "source_features.npy"
    target_feat_path = dirs["exp3_dann"] / "target_features.npy"
    if source_feat_path.exists() and target_feat_path.exists():
        _plot_tsne(source_feat_path, target_feat_path, figures_dir, source_name, target_name)

    # 5. Generate markdown report
    _generate_markdown_report(
        exp1_results, exp2_results, exp3_results,
        comparison_df, source_name, target_name, report_dir, figures_dir,
    )

    # 6. Generate LaTeX table
    if comparison_df is not None and not comparison_df.empty:
        _generate_latex_table(comparison_df, report_dir)

    print(f"[*] Report generation complete. Outputs in {dirs['root']}")


def _plot_comparison_chart(
    df: pd.DataFrame,
    figures_dir: Path,
    source_name: str,
    target_name: str,
) -> None:
    """Bar chart comparing F1, ROC-AUC, Balanced Accuracy across experiments."""
    print("[*] Generating comparison bar chart...")

    metrics_to_plot = [c for c in ["F1", "ROC_AUC", "Balanced_Accuracy", "PR_AUC", "Kappa"]
                       if c in df.columns]

    if not metrics_to_plot:
        return

    # Create grouped bar chart
    fig, axes = plt.subplots(1, len(metrics_to_plot), figsize=(5 * len(metrics_to_plot), 6))
    if len(metrics_to_plot) == 1:
        axes = [axes]

    colors = sns.color_palette("husl", n_colors=df["Experiment"].nunique())

    for ax, metric in zip(axes, metrics_to_plot):
        pivot = df.pivot_table(index="Model", columns="Experiment", values=metric, aggfunc="first")
        pivot.plot(kind="bar", ax=ax, color=colors[:pivot.shape[1]], width=0.7)
        ax.set_title(metric, fontsize=14, fontweight="bold")
        ax.set_ylabel("Score")
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=8, loc="lower right")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle(
        f"Cross-Dataset Performance: {source_name} → {target_name}",
        fontsize=16, fontweight="bold", y=1.02,
    )
    plt.tight_layout()

    for ext in ["png", "svg", "pdf"]:
        fig.savefig(figures_dir / f"comparison_chart.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def _plot_domain_auc_comparison(
    exp1: Optional[Dict],
    exp2: Optional[Dict],
    exp3: Optional[Dict],
    figures_dir: Path,
) -> None:
    """Bar chart comparing domain classifier AUC across experiments."""
    print("[*] Generating domain AUC comparison...")

    domain_aucs = {}

    if exp2 and "_domain_invariance" in exp2:
        domain_aucs["Exp2: Aligned\n(Raw Features)"] = exp2["_domain_invariance"].get("domain_auc_mean", 0)

    if exp3 and "_domain_invariance" in exp3:
        domain_aucs["Exp3: DANN\n(Adapted Features)"] = exp3["_domain_invariance"].get("domain_auc_mean", 0)

    if not domain_aucs:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(domain_aucs.keys(), domain_aucs.values(),
                  color=["#e74c3c", "#2ecc71"][:len(domain_aucs)], width=0.5)

    # Reference line at 0.5 (perfect domain invariance)
    ax.axhline(y=0.5, color="gray", linestyle="--", linewidth=1, label="Perfect Invariance (0.5)")

    ax.set_ylabel("Domain Classifier AUC", fontsize=12)
    ax.set_title("Domain Invariance Evaluation\n(Lower = Better Adaptation)", fontsize=14, fontweight="bold")
    ax.set_ylim(0, 1.0)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Add value labels on bars
    for bar, val in zip(bars, domain_aucs.values()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", va="bottom", fontweight="bold")

    plt.tight_layout()
    for ext in ["png", "svg", "pdf"]:
        fig.savefig(figures_dir / f"domain_auc_comparison.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def _plot_dann_training_curves(history_path: Path, figures_dir: Path) -> None:
    """Plot DANN training loss curves over epochs."""
    print("[*] Generating DANN training curves...")

    with open(history_path) as f:
        history = json.load(f)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Label loss
    if "label_losses" in history:
        axes[0].plot(history["label_losses"], color="#3498db", linewidth=2)
        axes[0].set_title("Label Classification Loss", fontweight="bold")
        axes[0].set_xlabel("Epoch")
        axes[0].set_ylabel("BCE Loss")
        axes[0].grid(alpha=0.3)

    # Domain loss
    if "domain_losses" in history:
        axes[1].plot(history["domain_losses"], color="#e74c3c", linewidth=2)
        axes[1].set_title("Domain Classification Loss", fontweight="bold")
        axes[1].set_xlabel("Epoch")
        axes[1].set_ylabel("BCE Loss")
        axes[1].grid(alpha=0.3)

    # Lambda schedule
    if "lambdas" in history:
        axes[2].plot(history["lambdas"], color="#2ecc71", linewidth=2)
        axes[2].set_title("GRL Lambda Schedule", fontweight="bold")
        axes[2].set_xlabel("Epoch")
        axes[2].set_ylabel("λ")
        axes[2].grid(alpha=0.3)

    fig.suptitle("DANN Training Progress", fontsize=16, fontweight="bold")
    plt.tight_layout()

    for ext in ["png", "svg", "pdf"]:
        fig.savefig(figures_dir / f"dann_training_curves.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def _plot_tsne(
    source_path: Path,
    target_path: Path,
    figures_dir: Path,
    source_name: str,
    target_name: str,
) -> None:
    """t-SNE visualization of DANN feature representations."""
    print("[*] Generating t-SNE visualization...")

    source_features = np.load(source_path)
    target_features = np.load(target_path)

    # Subsample for speed
    max_samples = 3000
    if len(source_features) > max_samples:
        idx = np.random.RandomState(42).choice(len(source_features), max_samples, replace=False)
        source_features = source_features[idx]
    if len(target_features) > max_samples:
        idx = np.random.RandomState(42).choice(len(target_features), max_samples, replace=False)
        target_features = target_features[idx]

    combined = np.vstack([source_features, target_features])
    labels = np.array(
        [source_name] * len(source_features) + [target_name] * len(target_features)
    )

    try:
        from sklearn.manifold import TSNE
        tsne = TSNE(n_components=2, perplexity=30, random_state=42, max_iter=1000)
        embeddings = tsne.fit_transform(combined)

        fig, ax = plt.subplots(figsize=(10, 8))

        for label, color, marker in [
            (source_name, "#3498db", "o"),
            (target_name, "#e74c3c", "^"),
        ]:
            mask = labels == label
            ax.scatter(
                embeddings[mask, 0], embeddings[mask, 1],
                c=color, marker=marker, alpha=0.5, s=15, label=label,
            )

        ax.set_title(
            "t-SNE of DANN Feature Representations\n(Overlapping clusters = successful adaptation)",
            fontsize=14, fontweight="bold",
        )
        ax.legend(fontsize=12, markerscale=2)
        ax.set_xlabel("t-SNE Dimension 1")
        ax.set_ylabel("t-SNE Dimension 2")
        ax.grid(alpha=0.2)

        plt.tight_layout()
        for ext in ["png", "svg", "pdf"]:
            fig.savefig(figures_dir / f"tsne_representations.{ext}", dpi=300, bbox_inches="tight")
        plt.close(fig)

    except Exception as e:
        print(f"[!] t-SNE visualization failed: {e}")


def _generate_markdown_report(
    exp1: Optional[Dict],
    exp2: Optional[Dict],
    exp3: Optional[Dict],
    comparison_df: Optional[pd.DataFrame],
    source_name: str,
    target_name: str,
    report_dir: Path,
    figures_dir: Path,
) -> None:
    """Generate a comprehensive markdown report."""
    print("[*] Generating markdown report...")

    lines = [
        f"# ARGUS Domain Adaptation Report",
        f"",
        f"**Source Dataset:** {source_name}",
        f"**Target Dataset:** {target_name}",
        f"**Generated:** {pd.Timestamp.now().isoformat()}",
        f"",
        f"---",
        f"",
        f"## Executive Summary",
        f"",
        f"This report evaluates three approaches to cross-dataset threat detection:",
        f"1. **Baseline (Exp 1):** Train on source with zero-padded features — no adaptation",
        f"2. **Aligned Baseline (Exp 2):** Map both datasets to a Unified Feature Schema",
        f"3. **DANN (Exp 3):** Domain-Adversarial Neural Network with gradient reversal",
        f"",
    ]

    # Results table
    if comparison_df is not None and not comparison_df.empty:
        lines.append("## Results")
        lines.append("")
        lines.append(comparison_df.to_markdown(index=False))
        lines.append("")

    # Domain invariance
    lines.append("## Domain Invariance Analysis")
    lines.append("")

    if exp2 and "_domain_invariance" in exp2:
        di = exp2["_domain_invariance"]
        lines.append(f"**Aligned Features (Exp 2):** Domain AUC = {di.get('domain_auc_mean', 'N/A'):.4f}")
        lines.append(f"  - {di.get('verdict', 'N/A')}")
        lines.append("")

    if exp3 and "_domain_invariance" in exp3:
        di = exp3["_domain_invariance"]
        lines.append(f"**DANN Representations (Exp 3):** Domain AUC = {di.get('domain_auc_mean', 'N/A'):.4f}")
        lines.append(f"  - {di.get('verdict', 'N/A')}")
        lines.append("")

    # Key insight
    lines.extend([
        "## Key Insight",
        "",
        "If the DANN's domain classifier AUC is closer to 0.5 than the aligned baseline's,",
        "AND the DANN's task F1 is higher than the aligned baseline's,",
        "then domain adaptation is working: the model has learned domain-invariant threat representations.",
        "",
        "This is the evidence needed to position ARGUS as a **domain-adaptive cyber-defense architecture**.",
        "",
        "## Figures",
        "",
    ])

    # Embed figure references
    for fig_name in ["comparison_chart.png", "domain_auc_comparison.png",
                     "dann_training_curves.png", "tsne_representations.png"]:
        fig_path = figures_dir / fig_name
        if fig_path.exists():
            lines.append(f"![{fig_name.replace('.png', '').replace('_', ' ').title()}]({fig_path})")
            lines.append("")

    report_path = report_dir / "domain_adaptation_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    print(f"[*] Markdown report saved to {report_path}")


def _generate_latex_table(df: pd.DataFrame, report_dir: Path) -> None:
    """Generate a LaTeX table for paper inclusion."""
    print("[*] Generating LaTeX table...")

    metrics_cols = [c for c in ["F1", "ROC_AUC", "Balanced_Accuracy", "PR_AUC", "Kappa", "domain_auc"]
                    if c in df.columns]

    if not metrics_cols:
        return

    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Cross-Dataset Generalization Performance}",
        r"\label{tab:domain_adaptation}",
        r"\begin{tabular}{ll" + "c" * len(metrics_cols) + "}",
        r"\toprule",
        "Approach & Model & " + " & ".join(metrics_cols) + r" \\",
        r"\midrule",
    ]

    for _, row in df.iterrows():
        approach = row.get("Approach", row.get("Experiment", ""))
        model = row.get("Model", "")
        vals = " & ".join(f"{row.get(c, 0):.3f}" if isinstance(row.get(c, 0), float) else str(row.get(c, "-"))
                          for c in metrics_cols)
        lines.append(f"{approach} & {model} & {vals}" + r" \\")

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])

    latex_path = report_dir / "results_table.tex"
    with open(latex_path, "w") as f:
        f.write("\n".join(lines))

    print(f"[*] LaTeX table saved to {latex_path}")


if __name__ == "__main__":
    print("This module is imported by domain_adaptation_experiment.py")
    print("Run: python training/scripts/domain_adaptation_experiment.py --help")
