import React from 'react';
import { Card } from '../../components/Card';
import { ShieldCheck, AlertOctagon, FileWarning, Dna, Info } from 'lucide-react';

export default function ProtocolLimitsPage() {
  return (
    <div className="space-y-6 pb-12 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100 font-mono flex items-center gap-2">
          <ShieldCheck className="w-6 h-6 text-cyan-400" />
          <span>Protocol, Verification & Known Limitations</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Complete disclosure of verified facts, diagnostic ceilings, unresolved discrepancies, and reproducibility protocols underlying ARGUS.
        </p>
      </div>

      {/* Section 1: Verified Final Results */}
      <Card className="space-y-4 border-emerald-500/30 bg-emerald-950/10">
        <h2 className="text-base font-bold font-mono text-emerald-400 flex items-center gap-2">
          <ShieldCheck className="w-5 h-5" />
          <span>Verified Final Results (What To Trust)</span>
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          Results carrying the <strong>Verified Final</strong> badge have passed strict zero-shot leakage protocols. Target domain adaptation was strictly unsupervised, calibration threshold selection ($\tau$) occurred on a disjoint split, and evaluation was locked to the holdout test set ($N=2.62M$ for D2). 
        </p>
        <ul className="text-xs text-slate-300 font-mono list-disc pl-5 space-y-2">
          <li><strong>Clean Class-Aware CORAL (D2)</strong>: Verified leakage-controlled baseline in <code>five_model_complete_comparison.csv</code>.</li>
          <li><strong>DANN (D2)</strong>: Verified collapsed performance accurately tracked in <code>dann_final_test_metrics.csv</code> and raw predictions.</li>
          <li><strong>D3 Native Models</strong>: Operational threshold sweeps in <code>d3_native_threshold_sweep.csv</code> evaluated under zero-leakage frozen constraints.</li>
        </ul>
      </Card>

      {/* Section 2: Diagnostic-Only Results */}
      <Card className="space-y-4 border-amber-500/30 bg-amber-950/10">
        <h2 className="text-base font-bold font-mono text-amber-400 flex items-center gap-2">
          <AlertOctagon className="w-5 h-5" />
          <span>Diagnostic-Only Results (What NOT To Cite As Final)</span>
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          Results marked as <strong>Diagnostic</strong> are theoretical upper-bounds or ablation checks. They explicitly violate the zero-shot assumption and must not be cited as the system's operational capability.
        </p>
        <ul className="text-xs text-slate-300 font-mono list-disc pl-5 space-y-2">
          <li><strong>Diagnostic Class-Aware CORAL</strong>: Found in <code>five_model_complete_comparison.csv</code>. This model used target labels during the alignment phase to perfectly pair source and target classes, calculating an artificial alignment ceiling. It also defaults to an uncalibrated 0.50 diagnostic threshold.</li>
        </ul>
      </Card>

      {/* Section 3: Known Open Issues */}
      <Card className="space-y-4 border-rose-500/30 bg-rose-950/10">
        <h2 className="text-base font-bold font-mono text-rose-400 flex items-center gap-2">
          <FileWarning className="w-5 h-5" />
          <span>Known Open Verification Issues</span>
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          The following discrepancies were explicitly documented during forensic verification sweeps and remain actively unresolved or structurally acknowledged.
        </p>
        <div className="space-y-4">
          <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <h4 className="text-xs font-bold text-rose-300 font-mono mb-1">DANN Narrative vs Raw Metric Discrepancy</h4>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Two source files disagree on DANN's performance: an unverified early draft (<code>ARGUS_RESULTS_README.txt</code>) claims ROC-AUC 0.5225, Specificity 1.084%, MCC 0.0885. However, recomputation from the raw probabilities (<code>dann_final_test_predictions.csv</code>) definitively proves ROC-AUC 0.332095, Specificity 0.064%, MCC 0.0128. 
              <br/><br/>
              <strong>Resolution Status:</strong> Unresolved internally, but the UI strictly enforces the recomputed raw values (0.332095).
            </p>
          </div>
          <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <h4 className="text-xs font-bold text-rose-300 font-mono mb-1">Feature Space Target Vector Condensation & Leakage</h4>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              <strong>Overlap Leakage:</strong> Forensic analysis confirmed astronomical internal duplication and explicit cross-domain overlap. 7 target vectors leaked (Overlap_NFT_vs_BoT=3, Overlap_CIC_vs_NFT=4). 
              <br/><br/>
              <strong>V1 Representation Limits:</strong> The legacy V1 4-feature space suffered extreme condensation, collapsing 1,000,000 BoT-IoT target records into only 82 unique vectors, crippling statistical generalizability. 
              <br/><br/>
              <strong>Resolution Status:</strong> Addressed in V2 neural experiments, but legacy models exposed in the UI still reflect the condensed V1 representation.
            </p>
          </div>
          <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <h4 className="text-xs font-bold text-rose-300 font-mono mb-1">Threshold / Hyperparameter Reproducibility</h4>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              <strong>Resolution Status:</strong> None documented for deployed legacy models. <code>docs/experiments/reproducibility_audit.md</code> states that a researcher can definitively reproduce major experiments using only the repo.
            </p>
          </div>
        </div>
      </Card>

      {/* Section 4: Reproducibility Notes */}
      <Card className="space-y-4 border-cyan-500/30">
        <h2 className="text-base font-bold font-mono text-cyan-400 flex items-center gap-2">
          <Dna className="w-5 h-5" />
          <span>Reproducibility & Statistical Limits</span>
        </h2>
        <ul className="text-xs text-slate-300 font-mono list-disc pl-5 space-y-2">
          <li><strong>Single-Seed Evaluation:</strong> The deployed Phase 1 legacy baseline models (e.g., XGBoost, Clean CORAL, D3 Native) shown in the Live Monitor utilize a single fixed seed (Seed 42) for deterministic data partitioning and tree construction. These point estimates lack multi-seed variance bars.</li>
          <li><strong>V2 Benchmarks (Multi-seed):</strong> Multiseed variance (Seeds 42-46) is exclusively reserved for the V2 neural experiments (e.g., Attention / Lightweight Transformer), which are frozen structurally but not surfaced for real-time inference in this dashboard.</li>
        </ul>
      </Card>
    </div>
  );
}
