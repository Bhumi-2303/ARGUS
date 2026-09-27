import { ModelStatusBadge } from '../../components/ModelStatusBadge';
import { MetricInfoIcon } from '../../components/MetricInfoIcon';
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import {
  BarChart3,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Layers,
} from 'lucide-react';
import { api } from '../../api/client';
import { ProvenanceBadge } from '../../components/ProvenanceBadge';
import { Card } from '../../components/Card';
import { Skeleton } from '../../components/Skeleton';

export interface BenchmarkRow {
  model_name: string;
  domain?: string;
  accuracy?: number;
  f1_score?: number;
  mcc?: number;
  precision?: number;
  recall?: number;
  specificity?: number;
  fpr?: number;
  fnr?: number;
  threshold?: number;
  protocol_status?: string;
  [key: string]: any;
}

export default function ModelComparisonPage() {
  const [sortField, setSortField] = useState<keyof BenchmarkRow | string>('mcc');
  const [sortAsc, setSortAsc] = useState<boolean>(false);
  const [showDiagnostic, setShowDiagnostic] = useState<boolean>(false);

  // Fetch verified main results table
  const { data: verifiedData, isLoading: loadingVerified } = useQuery({
    queryKey: ['five_model_complete_comparison'],
    queryFn: () => api.getResultTable('five_model_complete_comparison'),
  });

  // Fetch models info for frozen thresholds
  const { data: modelsInfo } = useQuery({
    queryKey: ['models_info'],
    queryFn: () => api.getModels(),
  });

  // Fetch diagnostic table for collapsed panel
  const { data: diagnosticData, isLoading: loadingDiagnostic } = useQuery({
    queryKey: ['diagnostic_class_aware_coral'],
    queryFn: () => api.getResultTable('diagnostic_class_aware_coral'),
    enabled: showDiagnostic,
  });

  const rawRows: BenchmarkRow[] = (verifiedData?.data as BenchmarkRow[]) || [];

  // Map threshold from models API if available
  const rows: BenchmarkRow[] = rawRows.map((r) => {
    const matchedModel = modelsInfo?.models.find((m) => m.model_id === r.model_name || m.name === r.model_name || m.name === r.Model);
    return {
      ...r,
      model_name: r.Model || r.model_name || 'Unknown',
      threshold: matchedModel?.threshold ?? r.Threshold ?? r.Threshold ?? 0.50,
      protocol_status: matchedModel?.protocol_status || r.Protocol_Status || (r.Model?.includes('DANN') ? 'dann_adapted' : 'final'),
      modelInfo: matchedModel,
    };
  });


  // Sort rows
  const sortedRows: BenchmarkRow[] = [...rows].sort((a, b) => {
    const valA = a[sortField] ?? 0;
    const valB = b[sortField] ?? 0;
    return sortAsc ? (valA > valB ? 1 : -1) : valA < valB ? 1 : -1;
  });

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  // Radar Chart option comparing models
  const radarChartOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    legend: { textStyle: { color: '#94a3b8' }, top: 0 },
    radar: {
      indicator: [
        { name: 'MCC', max: 1 },
        { name: 'F1 Score', max: 1 },
        { name: 'Specificity', max: 1 },
        { name: 'Recall', max: 1 },
        { name: 'Accuracy', max: 1 },
      ],
      axisName: { color: '#94a3b8', fontSize: 11, fontFamily: 'monospace' },
      splitLine: { lineStyle: { color: '#334155' } },
      splitArea: { areaStyle: { color: ['rgba(30,41,59,0.4)', 'rgba(15,23,42,0.6)'] } },
    },
    series: [
      {
        name: 'Architecture Performance',
        type: 'radar',
        data: sortedRows.map((r, i) => {
          const colors = ['#f43f5e', '#3b82f6', '#10b981', '#f59e0b'];
          return {
            value: [
              r.MCC ?? 0,
              r.F1 ?? 0,
              r.Specificity ?? 0,
              r.Recall ?? 0,
              r.Accuracy ?? 0,
            ],
            name: r.model_name,
            itemStyle: { color: colors[i % colors.length] },
          };
        }),
      },
    ],
  };

  return (
    <div className="space-y-8 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100 font-mono flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-cyan-400" />
            <span>Cross-Domain Model Comparison & Empirical Benchmark</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Authoritative empirical performance matrix across Source-Only, Global CORAL, Clean Class-Aware CORAL, and DANN models.
          </p>
        </div>

        <ProvenanceBadge
          sourceFile={verifiedData?.source_file || 'results/verified/five_model_complete_comparison.csv'}
          protocolStatus="final"
        />
      </div>

      {/* DANN Degenerate-Risk Warning Alert */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/40 text-amber-300 flex items-start gap-3 shadow-lg">
        <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs font-mono">
          <div className="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <span>DEGENERATE-RISK WARNING: DANN ADVERSARIAL REPRESENTATION COLLAPSE</span>
            <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px]">
              MCC: {(() => { const dann = rows.find(r => r.model_name?.toLowerCase().includes('dann') || r.Model?.toLowerCase().includes('dann')); return typeof dann?.MCC === 'number' ? dann.MCC.toFixed(4) : typeof dann?.mcc === 'number' ? dann.mcc.toFixed(4) : '-'; })()}
            </span>
          </div>

          <p className="text-amber-200/90 leading-relaxed font-sans">
            Under severe target class imbalance (e.g. 93% attack flows in NF-ToN-IoT-v2 or 82% benign in IEC 104), DANN gradient reversal forces feature representation collapse, causing the model to predict 100% majority class. High nominal F1/accuracy masks complete loss of discriminative power (MCC = 0.0129).
          </p>

        </div>
      </div>

      {/* Sortable Main Performance Table */}
      <Card className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold font-mono text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" />
            <span>Verified 4-Architecture Performance Matrix</span>
          </h2>
          <span className="text-xs text-slate-400 font-mono">
            Click table headers to sort metrics
          </span>
        </div>

        {loadingVerified ? (
          <Skeleton className="h-48 w-full" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs text-slate-300">
              <thead className="bg-slate-950 border-b border-slate-800 text-[11px] text-slate-400 uppercase">
                <tr>
                  <th className="p-3">Model Architecture</th>
                  <th
                    onClick={() => handleSort('mcc')}
                    className="p-3 cursor-pointer hover:text-cyan-300 transition-colors"
                  >
                    MCC {sortField === 'mcc' && (sortAsc ? '▲' : '▼')}
                  </th>
                  <th
                    onClick={() => handleSort('f1_score')}
                    className="p-3 cursor-pointer hover:text-cyan-300 transition-colors"
                  >
                    F1 Score {sortField === 'f1_score' && (sortAsc ? '▲' : '▼')}
                  </th>
                  <th
                    onClick={() => handleSort('accuracy')}
                    className="p-3 cursor-pointer hover:text-cyan-300 transition-colors"
                  >
                    Accuracy {sortField === 'accuracy' && (sortAsc ? '▲' : '▼')}
                  </th>
                  <th
                    onClick={() => handleSort('recall')}
                    className="p-3 cursor-pointer hover:text-cyan-300 transition-colors"
                  >
                    Recall (TPR) {sortField === 'recall' && (sortAsc ? '▲' : '▼')}
                  </th>
                  <th
                    onClick={() => handleSort('fpr')}
                    className="p-3 cursor-pointer hover:text-cyan-300 transition-colors"
                  >
                    FPR {sortField === 'fpr' && (sortAsc ? '▲' : '▼')}
                  </th>
                  <th className="p-3">Frozen Threshold (\(\tau\))</th>
                  <th className="p-3">Data Provenance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {sortedRows.map((r) => {
                  const isDANN = r.model_name?.includes('dann');
                  const isBest = r.model_name?.includes('d2_coral');

                  return (
                    <tr
                      key={r.model_name}
                      className={`hover:bg-slate-900/50 transition-colors ${
                        isDANN ? 'bg-amber-500/5' : isBest ? 'bg-cyan-500/5' : ''
                      }`}
                    >
                      <td className="p-3 font-bold">
                        <div className="flex items-center gap-2">
                          <span className={isBest ? 'text-cyan-300' : isDANN ? 'text-amber-400' : 'text-slate-200'}>
                            {r.model_name}
                          </span>
                          {isBest && (
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-cyan-500/20 text-cyan-300">
                              BEST
                            </span>
                          )}
                          {isDANN && (
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-500/20 text-amber-300">
                              DEGENERATE
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="p-3">
                        <span
                          className={`font-extrabold ${
                            isDANN
                              ? 'text-rose-400'
                              : (r.MCC ?? 0) > 0.9
                              ? 'text-emerald-400'
                              : 'text-amber-400'
                          }`}
                        >
                          {typeof r.MCC === 'number' ? r.MCC.toFixed(4) : '-'}
                        </span>
                      </td>
                      <td className="p-3 font-bold text-slate-200">
                        {typeof r.F1 === 'number' ? r.F1.toFixed(4) : '-'}
                      </td>
                      <td className="p-3 text-slate-300">
                        {typeof r.Accuracy === 'number' ? r.Accuracy.toFixed(4) : '-'}
                      </td>
                      <td className="p-3 text-blue-400 font-bold">
                        {typeof r.Recall === 'number' ? r.Recall.toFixed(4) : '-'}
                      </td>
                      <td className="p-3 font-bold text-rose-400">
                        {typeof r.Specificity === 'number' ? (1 - r.Specificity).toFixed(4) : '-'}
                      </td>
                      <td className="p-3 font-mono text-cyan-300">
                        \(\tau\) = {r.Threshold?.toFixed(2)}
                      </td>
                      <td className="p-3">
                        <ProvenanceBadge
                          sourceFile={verifiedData?.source_file || 'results/verified/five_model_complete_comparison.csv'}
                          protocolStatus="final"
                          compact
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Radar Chart & Confusion Matrix Side-by-Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="space-y-3">
          <h3 className="text-sm font-bold font-mono text-slate-900 dark:text-slate-100">
            Multi-Metric Radar Comparison Across Architectures
          </h3>
          <div className="h-72 w-full">
            <ReactECharts option={radarChartOption} style={{ height: '100%', width: '100%' }} />
          </div>
        </Card>

        {/* Confusion Matrices Grid */}
        <Card className="space-y-3">
          <h3 className="text-sm font-bold font-mono text-slate-900 dark:text-slate-100">
            Target Confusion Matrices per Architecture
          </h3>

          <div className="grid grid-cols-2 gap-3 pt-2">
            {sortedRows.map((r) => {
              const tpPct = typeof r.Recall === 'number' ? (r.Recall * 100).toFixed(0) : '-';
              const fpPct = typeof r.Specificity === 'number' ? ((1 - r.Specificity) * 100).toFixed(0) : '-';
              const tnPct = typeof r.Specificity === 'number' ? (r.Specificity * 100).toFixed(0) : '-';
              const fnPct = typeof r.Recall === 'number' ? ((1 - r.Recall) * 100).toFixed(0) : '-';

              return (
                <div key={r.model_name} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2 font-mono text-xs">
                  <div className="flex justify-between items-center text-[11px] font-bold text-cyan-300 truncate">
                    <span className="truncate">{r.model_name}</span>
                    <span className="text-[10px] text-slate-400">\(\tau\)={r.Threshold?.toFixed(2)}</span>
                  </div>

                  <div className="grid grid-cols-2 gap-1 text-[10px] text-center">
                    <div className="p-1.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                      <span className="block text-slate-400 text-[9px]">TN</span>
                      <span className="font-bold">{tnPct}%</span>
                    </div>
                    <div className="p-1.5 rounded bg-rose-500/10 border border-rose-500/20 text-rose-300">
                      <span className="block text-slate-400 text-[9px]">FP</span>
                      <span className="font-bold">{fpPct}%</span>
                    </div>
                    <div className="p-1.5 rounded bg-rose-500/10 border border-rose-500/20 text-rose-300">
                      <span className="block text-slate-400 text-[9px]">FN</span>
                      <span className="font-bold">{fnPct}%</span>
                    </div>
                    <div className="p-1.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-300">
                      <span className="block text-slate-400 text-[9px]">TP</span>
                      <span className="font-bold">{tpPct}%</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      {/* Collapsible Diagnostic Run Panel */}
      <Card className="space-y-4 border-amber-500/30">
        <button
          onClick={() => setShowDiagnostic(!showDiagnostic)}
          className="w-full flex items-center justify-between font-mono text-sm font-bold text-amber-300 hover:text-amber-200 focus:outline-none"
        >
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>diagnostic (not a final result) - Unverified Exploratory Runs</span>
          </div>
          {showDiagnostic ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showDiagnostic && (
          <div className="space-y-3 pt-2 border-t border-slate-800 animate-in fade-in duration-200">
            <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-xs text-amber-200 leading-relaxed font-sans">
              <strong>Notice:</strong> The table below displays diagnostic-only exploratory runs from early hyperparameter sweeps. These metrics are strictly excluded from verified paper benchmarks.
            </div>

            {loadingDiagnostic ? (
              <Skeleton className="h-32 w-full" />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left font-mono text-xs text-slate-300">
                  <thead className="bg-slate-950 border-b border-slate-800 text-[11px] text-amber-400 uppercase">
                    <tr>
                      <th className="p-2.5">Diagnostic Run Name</th>
                      <th className="p-2.5">Target MCC</th>
                      <th className="p-2.5">Target F1</th>
                      <th className="p-2.5">FPR</th>
                      <th className="p-2.5">Status</th>
                      <th className="p-2.5">Provenance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80">
                    {(diagnosticData?.data || []).map((dRow, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/50">
                        <td className="p-2.5 font-bold text-slate-200">
                          {dRow.run_name || dRow.model_name || `Diagnostic_Run_${idx + 1}`}
                        </td>
                        <td className="p-2.5 font-bold text-amber-400">
                          {typeof dRow.MCC === 'number' ? dRow.MCC.toFixed(4) : '-'}
                        </td>
                        <td className="p-2.5">{typeof dRow.F1 === 'number' ? dRow.F1.toFixed(4) : '-'}</td>
                        <td className="p-2.5 text-rose-400 font-bold">
                          {typeof dRow.Specificity === 'number' ? (1 - dRow.Specificity).toFixed(4) : '-'}
                        </td>
                        <td className="p-2.5">
                          <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold">
                            DIAGNOSTIC ONLY
                          </span>
                        </td>
                        <td className="p-2.5">
                          <ProvenanceBadge
                            sourceFile="results/diagnostic/diagnostic_class_aware_coral.csv"
                            protocolStatus="diagnostic-only"
                            compact
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}
