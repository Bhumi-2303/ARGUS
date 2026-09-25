import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, DomainInfo } from '../../api/client';
import {
  FileCheck2,
  AlertTriangle,
  Lock,
  Layers,
  ShieldCheck,
  CheckCircle2,
  Info,
  Database,
  HelpCircle,
} from 'lucide-react';
import { ProvenanceBadge } from '../../components/ProvenanceBadge';
import { Card } from '../../components/Card';


export default function ProtocolLimitsPage() {
  const leakageSplits = [
    {
      split_name: 'Source Training Split (D1)',
      dataset: 'CICIoT2023 (5.49M flows)',
      purpose: 'Supervised tree ensemble & feature extraction training',
      labels_used: 'YES (Supervised)',
      leakage_protection: 'Isolated to Source Domain D1',
    },
    {
      split_name: 'Target Adaptation Split (D2 / D3)',
      dataset: 'NF-ToN-IoT-v2 / IEC 60870-5-104',
      purpose: 'Unsupervised second-order CORAL covariance alignment (\(C_T\))',
      labels_used: 'NO (Unsupervised)',
      leakage_protection: 'Strictly zero ground-truth labels accessed',
    },
    {
      split_name: 'Target Calibration Split',
      dataset: 'Target Domain 20% Subset',
      purpose: 'Decision threshold (\(\tau\)) selection via argmax MCC sweep',
      labels_used: 'YES (Calibration only)',
      leakage_protection: 'Disjoint from holdout evaluation test set',
    },
    {
      split_name: 'Zero-Leakage Target Test Split',
      dataset: 'Target Domain Holdout (80%)',
      purpose: 'Final reported paper evaluation benchmark metrics',
      labels_used: 'YES (Evaluation only)',
      leakage_protection: 'Strictly frozen; zero modification allowed',
    },
  ];

  const { data: domainsData } = useQuery({
    queryKey: ['domains_limits'],
    queryFn: () => api.getDomains(),
  });

  const domainsList = domainsData?.domains || [];
  const ciciotDomain = domainsList.find((d: DomainInfo) => d.domain_id === 'ciciot');
  const nftonDomain = domainsList.find((d: DomainInfo) => d.domain_id === 'nfton');
  const iecDomain = domainsList.find((d: DomainInfo) => d.domain_id === 'iec104');


  const classPriorShift = [
    {
      domain: 'Domain 1: CICIoT2023 (Source)',
      environment: 'Enterprise IoT Network',
      attack_ratio: typeof ciciotDomain?.attack_ratio === 'number' ? `${(ciciotDomain.attack_ratio * 100).toFixed(1)}%` : '67.4%',
      benign_ratio: typeof ciciotDomain?.attack_ratio === 'number' ? `${((1 - ciciotDomain.attack_ratio) * 100).toFixed(1)}%` : '32.6%',
      class_imbalance: 'Moderate (2:1)',
    },
    {
      domain: 'Domain 2: NF-ToN-IoT-v2 (Target 1)',
      environment: 'Smart Home & Industrial NetFlow',
      attack_ratio: typeof nftonDomain?.attack_ratio === 'number' ? `${(nftonDomain.attack_ratio * 100).toFixed(1)}%` : '93.2%',
      benign_ratio: typeof nftonDomain?.attack_ratio === 'number' ? `${((1 - nftonDomain.attack_ratio) * 100).toFixed(1)}%` : '6.8%',
      class_imbalance: 'Extreme Attack-Heavy (14:1)',
    },
    {
      domain: 'Domain 3: IEC 60870-5-104 (Target 2)',
      environment: 'Power Substation SCADA ICS',
      attack_ratio: typeof iecDomain?.attack_ratio === 'number' ? `${(iecDomain.attack_ratio * 100).toFixed(1)}%` : '18.3%',
      benign_ratio: typeof iecDomain?.attack_ratio === 'number' ? `${((1 - iecDomain.attack_ratio) * 100).toFixed(1)}%` : '81.7%',
      class_imbalance: 'Extreme Benign-Heavy (4.5:1)',
    },

  ];


  return (
    <div className="space-y-8 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100 font-mono flex items-center gap-2">
            <FileCheck2 className="w-6 h-6 text-rose-400" />
            <span>Protocol Integrity, Data Leakage Controls & Known Limitations</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Transparent disclosure of split partitioning, zero data leakage controls, single-seed evaluation baseline, and dataset class-prior shift.
          </p>
        </div>

        <ProvenanceBadge
          sourceFile="results/verified/five_model_complete_comparison.csv"
          protocolStatus="final"
        />
      </div>

      {/* Section 1: Leakage-Control Split Partitioning Table */}
      <Card className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold font-mono text-slate-100 flex items-center gap-2">
            <Lock className="w-5 h-5 text-emerald-400" />
            <span>Strict Zero-Leakage Dataset Partitioning Protocol</span>
          </h2>
          <ProvenanceBadge
            sourceFile="results/verified/five_model_complete_comparison.csv"
            protocolStatus="final"
            compact
          />
        </div>

        <p className="text-xs text-slate-400">
          To prevent data leakage during domain adaptation, target adaptation is strictly unsupervised, calibration threshold selection occurs on a disjoint split, and evaluation is locked to the holdout test set.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs text-slate-300">
            <thead className="bg-slate-950 border-b border-slate-800 text-[11px] text-slate-400 uppercase">
              <tr>
                <th className="p-3">Partition Name</th>
                <th className="p-3">Underlying Dataset</th>
                <th className="p-3">Primary Purpose</th>
                <th className="p-3">Target Labels Used</th>
                <th className="p-3">Data Leakage Protection</th>
                <th className="p-3">Provenance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {leakageSplits.map((split, idx) => (
                <tr key={idx} className="hover:bg-slate-900/50">
                  <td className="p-3 font-bold text-cyan-300">{split.split_name}</td>
                  <td className="p-3 text-slate-200">{split.dataset}</td>
                  <td className="p-3 text-slate-300">{split.purpose}</td>
                  <td className="p-3 font-bold">
                    {split.labels_used.includes('NO') ? (
                      <span className="text-emerald-400">{split.labels_used}</span>
                    ) : (
                      <span className="text-amber-400">{split.labels_used}</span>
                    )}
                  </td>
                  <td className="p-3 font-bold text-cyan-400">{split.leakage_protection}</td>
                  <td className="p-3">
                    <ProvenanceBadge
                      sourceFile="results/verified/five_model_complete_comparison.csv"
                      protocolStatus="final"
                      compact
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Section 2: Single-Seed Baseline Disclosure */}
      <Card className="space-y-3 border-cyan-500/30">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold font-mono text-slate-100 flex items-center gap-2">
            <Info className="w-5 h-5 text-cyan-400" />
            <span>Single-Seed Evaluation Baseline Disclosure</span>
          </h3>
          <ProvenanceBadge
            sourceFile="results/verified/five_model_complete_comparison.csv"
            protocolStatus="final"
            compact
          />
        </div>

        <p className="text-xs text-slate-300 leading-relaxed font-mono">
          The primary reported paper benchmark results utilize a single fixed seed (Seed 42) for deterministic data partitioning and XGBoost / LightGBM tree construction. Multi-seed robustness sweeps (5 random seeds) are detailed in supplementary deliverables (<code>paper/ARGUS_Paper_Data/</code>) and exhibit an MCC standard deviation of \(\sigma &lt; 0.004\).
        </p>
      </Card>

      {/* Section 3: Dataset Class-Prior Shift Matrix */}
      <Card className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold font-mono text-slate-100 flex items-center gap-2">
            <Database className="w-5 h-5 text-amber-400" />
            <span>Dataset Class-Prior Shift Breakdown</span>
          </h2>
          <ProvenanceBadge
            sourceFile="data/samples/ciciot.parquet"
            protocolStatus="final"
            compact
          />
        </div>

        <p className="text-xs text-slate-400">
          Cross-domain deployment experiences severe prior probability shift (\(P(Y)\)), changing the optimal decision boundary \(\tau\).
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs text-slate-300">
            <thead className="bg-slate-950 border-b border-slate-800 text-[11px] text-slate-400 uppercase">
              <tr>
                <th className="p-3">Domain Name</th>
                <th className="p-3">Target Operational Environment</th>
                <th className="p-3">Attack Proportion (\(P(Y=1)\))</th>
                <th className="p-3">Benign Proportion (\(P(Y=0)\))</th>
                <th className="p-3">Imbalance Profile</th>
                <th className="p-3">Provenance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {classPriorShift.map((cps, idx) => (
                <tr key={idx} className="hover:bg-slate-900/50">
                  <td className="p-3 font-bold text-cyan-300">{cps.domain}</td>
                  <td className="p-3 text-slate-200">{cps.environment}</td>
                  <td className="p-3 font-bold text-rose-400">{cps.attack_ratio}</td>
                  <td className="p-3 font-bold text-emerald-400">{cps.benign_ratio}</td>
                  <td className="p-3 font-mono text-amber-400">{cps.class_imbalance}</td>
                  <td className="p-3">
                    <ProvenanceBadge sourceFile="data/samples/ciciot.parquet" protocolStatus="final" compact />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Section 4: Known Caveats & Honest Limitations */}
      <Card className="space-y-4 border-rose-500/30">
        <h2 className="text-base font-bold font-mono text-slate-100 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-rose-400" />
          <span>Known Limitations & Scientific Caveats</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
            <div className="font-bold text-cyan-300">1. Feature Resolution Limits</div>
            <p className="text-[11px] text-slate-400 leading-relaxed font-sans">
              Harmonization restricts feature space to 4 universal packet metrics. High-cardinality payload protocols may require extended feature representations.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
            <div className="font-bold text-amber-400">2. DANN Collapse Sensitivity</div>
            <p className="text-[11px] text-slate-400 leading-relaxed font-sans">
              Domain-Adversarial Neural Networks (DANN) suffer representation collapse under extreme label imbalance, resulting in 0.00 MCC on SCADA datasets.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
            <div className="font-bold text-rose-400">3. Non-Stationary Telemetry</div>
            <p className="text-[11px] text-slate-400 leading-relaxed font-sans">
              Substation physical operational state changes require continuous rolling CORAL covariance recalculation over time.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
