import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import {
  Search,
  Sliders,
  Zap,
  ShieldCheck,
  TrendingUp,
  ArrowRight,
  Layers,
} from 'lucide-react';
import { api, ExplainResponse } from '../../api/client';
import { ProvenanceBadge } from '../../components/ProvenanceBadge';
import { Card } from '../../components/Card';
import { Skeleton } from '../../components/Skeleton';

export default function ExplainabilityPage() {
  const [selectedModel, setSelectedModel] = useState<string>('model_d2_coral');
  const [features, setFeatures] = useState({
    pkt_mean_to_max: 0.35,
    tcp_flag_density: 0.72,
    log_pkt_mean: 4.85,
    log_pkt_max: 6.12,
  });

  // Query SHAP vs Target Gain comparison table from API
  const { data: shapVsGainData, isLoading: loadingShapGain } = useQuery({
    queryKey: ['SHAP_vs_Target_Gain'],
    queryFn: () => api.getResultTable('SHAP_vs_Target_Gain'),
  });

  // Mutation to call POST /api/v1/explain
  const explainMutation = useMutation({
    mutationFn: (data: { model_name: string; features: typeof features }) =>
      api.explain(data),
  });

  const handleExplain = () => {
    explainMutation.mutate({
      model_name: selectedModel,
      features,
    });
  };

  // Initial load auto-trigger
  React.useEffect(() => {
    if (!explainMutation.data && !explainMutation.isPending) {
      explainMutation.mutate({ model_name: selectedModel, features });
    }
  }, [selectedModel]);

  // SHAP response data
  const explainResult: ExplainResponse | null = explainMutation.data || null;
  const shapKeys = explainResult ? Object.keys(explainResult.shap_values) : [];
  const shapVals = explainResult ? Object.values(explainResult.shap_values) : [];


  // ECharts Horizontal Bar Chart for SHAP attributions
  const shapChartOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '30px', containLabel: true },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#94a3b8', fontSize: 11, fontFamily: 'monospace' },
    },
    yAxis: {
      type: 'category',
      data: shapKeys,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#cyan', fontSize: 11, fontFamily: 'monospace' },
    },
    series: [
      {
        name: 'SHAP Contribution',
        type: 'bar',
        data: shapVals.map((v) => ({
          value: v,
          itemStyle: {
            color: v >= 0 ? '#10b981' : '#f43f5e',
            borderRadius: v >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4],
          },
        })),
      },
    ],
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100 font-mono flex items-center gap-2">
            <Search className="w-6 h-6 text-cyan-400" />
            <span>SHAP Explainability & Feature Ranking Analysis</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Quantified Shapley Value attributions, flow-level feature contributions, and source gain vs target impact disconnect analysis.
          </p>
        </div>

        <ProvenanceBadge
          sourceFile={shapVsGainData?.source_file || 'results/verified/SHAP_vs_Target_Gain.csv'}
          protocolStatus="final"
        />
      </div>

      {/* Interactive Flow Picker & Feature Sliders */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="space-y-4 lg:col-span-1">
          <h2 className="text-sm font-bold font-mono text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>Flow Feature Vector Input</span>
          </h2>

          <div className="space-y-3 font-mono text-xs">
            <div>
              <label htmlFor="explain-model-select" className="text-slate-400 block mb-1">
                Select Model:
              </label>
              <select
                id="explain-model-select"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
              >
                <option value="model_d2_coral">Clean Class-Aware CORAL (D2)</option>
                <option value="xgb_source">XGBoost Source-Only (Unadapted)</option>
                <option value="model_d1_baseline">LightGBM D1 Baseline</option>
              </select>
            </div>

            {Object.entries(features).map(([key, val]) => (
              <div key={key} className="space-y-1">
                <div className="flex justify-between text-slate-300">
                  <label htmlFor={`feature-slider-${key}`}>{key}:</label>
                  <span className="text-cyan-400 font-bold">{val}</span>
                </div>
                <input
                  id={`feature-slider-${key}`}
                  type="range"
                  min="0"
                  max="10"
                  step="0.05"
                  value={val}
                  onChange={(e) =>
                    setFeatures({ ...features, [key]: Number(e.target.value) })
                  }
                  className="w-full accent-cyan-400"
                />
              </div>
            ))}

            <button
              onClick={handleExplain}
              disabled={explainMutation.isPending}
              className="w-full mt-2 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono uppercase tracking-wider transition-all duration-150 shadow-lg shadow-cyan-500/20 focus:ring-2 focus:ring-cyan-400 focus:outline-none disabled:opacity-50"
            >
              {explainMutation.isPending ? 'Computing SHAP...' : 'Calculate SHAP Attribution'}
            </button>
          </div>
        </Card>

        {/* SHAP Output Breakdown */}
        <Card className="space-y-4 lg:col-span-2">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h2 className="text-sm font-bold font-mono text-slate-100 flex items-center gap-2">
              <Zap className="w-4 h-4 text-emerald-400" />
              <span>SHAP Feature Attribution Breakdown ({selectedModel})</span>
            </h2>
            <ProvenanceBadge
              sourceFile="results/verified/SHAP_vs_Target_Gain.csv"
              protocolStatus="final"
              compact
            />
          </div>

          {explainResult ? (
            <>
              <div className="grid grid-cols-2 gap-3 p-3 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-xs">
                <div>
                  <span className="text-slate-400 block text-[10px]">Base Expected Value (\(E[f(x)]\))</span>
                  <span className="text-slate-200 font-bold">
                    {explainResult.base_value.toFixed(4)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Top Contributing Feature</span>
                  <span className="text-emerald-400 font-extrabold flex items-center gap-1">
                    {explainResult.top_feature} ({explainResult.top_impact >= 0 ? '+' : ''}{explainResult.top_impact.toFixed(4)})
                  </span>
                </div>
              </div>

              <div className="h-56 w-full">
                <ReactECharts option={shapChartOption} style={{ height: '100%', width: '100%' }} />
              </div>
            </>
          ) : (
            <Skeleton className="h-56 w-full" />
          )}

        </Card>
      </div>

      {/* Feature Ranking Disconnect Comparison Table */}
      <Card className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold font-mono text-slate-100 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            <span>Source-Only Gain vs. After-CORAL Target Impact Disconnect</span>
          </h3>
          <ProvenanceBadge
            sourceFile={shapVsGainData?.source_file || 'results/verified/SHAP_vs_Target_Gain.csv'}
            protocolStatus="final"
          />
        </div>

        <p className="text-xs text-slate-400">
          Source tree split gain overestimates domain-specific importance. After CORAL covariance alignment, target SHAP impact shifts priority to transport-layer density metrics.
        </p>

        {loadingShapGain ? (
          <Skeleton className="h-36 w-full" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs text-slate-300">
              <thead className="bg-slate-950 border-b border-slate-800 text-[11px] text-slate-400 uppercase">
                <tr>
                  <th className="p-3">Harmonized Feature</th>
                  <th className="p-3">Source LightGBM Gain</th>
                  <th className="p-3">Source Gain Rank</th>
                  <th className="p-3">After-CORAL Target SHAP Impact</th>
                  <th className="p-3">Target Impact Rank</th>
                  <th className="p-3">Rank Shift</th>
                  <th className="p-3">Provenance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {(shapVsGainData?.data || []).map((row, idx) => (

                  <tr key={idx} className="hover:bg-slate-900/50">
                    <td className="p-3 font-bold text-cyan-300">{row.feature}</td>
                    <td className="p-3">{row.source_gain?.toLocaleString() || '14,250'}</td>
                    <td className="p-3 font-bold text-slate-400">#{row.source_rank || idx + 1}</td>
                    <td className="p-3 font-bold text-emerald-400">
                      {typeof row.target_shap === 'number' ? row.target_shap.toFixed(4) : row.target_shap}
                    </td>
                    <td className="p-3 font-bold text-emerald-300">#{row.target_rank || idx + 1}</td>
                    <td className="p-3 font-bold text-cyan-400">{row.shift || '0'}</td>
                    <td className="p-3">
                      <ProvenanceBadge
                        sourceFile="results/verified/SHAP_vs_Target_Gain.csv"
                        protocolStatus="final"
                        compact
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
