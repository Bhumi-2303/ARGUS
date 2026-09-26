import React, { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import {
  Play,
  Pause,
  RotateCcw,
  Sliders,
  AlertTriangle,
  Activity,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Clock,
} from 'lucide-react';
import { api, ShiftResponse } from '../../api/client';
import { ProvenanceBadge } from '../../components/ProvenanceBadge';
import { Card } from '../../components/Card';

interface StreamFlowEvent {
  event_id: string;
  timestamp: string;
  domain: string;
  features: Record<string, number>;
  true_label: number;
  predictions: Record<
    string,
    {
      probability: number;
      label: number;
    }
  >;
}

interface ModelMetricsAccumulator {
  tp: number;
  fp: number;
  tn: number;
  fn: number;
}

export default function LiveMonitorPage() {
  // Stream Controls State
  const [selectedDomain, setSelectedDomain] = useState<string>('nfton');
  const [selectedModels, setSelectedModels] = useState<string[]>([
    'model_d2_coral',
    'xgb_source',
  ]);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [speed, setSpeed] = useState<number>(10);
  const [seed, setSeed] = useState<number>(42);

  // Stream data state
  const [flowHistory, setFlowHistory] = useState<StreamFlowEvent[]>([]);
  const [shiftAlert, setShiftAlert] = useState<ShiftResponse | null>(null);
  const [showShiftBanner, setShowShiftBanner] = useState<boolean>(false);

  // Model statistics map
  const [modelStats, setModelStats] = useState<Record<string, ModelMetricsAccumulator>>({});

  const eventSourceRef = useRef<EventSource | null>(null);

  // Available domain options
  const domainOptions = [
    { id: 'nfton', name: 'NF-ToN-IoT-v2 (Target Smart Home)' },
    { id: 'iec104', name: 'IEC 60870-5-104 (Target SCADA Substation)' },
    { id: 'ciciot', name: 'CICIoT2023 (Source Enterprise)' },
  ];

  // Available model options
  const modelOptions = [
    { id: 'model_d2_coral', name: 'Clean Class-Aware CORAL (D2)' },
    { id: 'xgb_source', name: 'XGBoost Source-Only (Unadapted)' },
    { id: 'model_d1_baseline', name: 'LightGBM D1 Baseline' },
    { id: 'model_d3_native', name: 'D3 Native SCADA Model' },
  ];

  // Domain shift query for checking drift on domain change
  const checkDomainShift = async (newDomain: string) => {
    try {
      const res = await api.getShift(newDomain, 1000);
      if (res.domain_shift) {
        setShiftAlert(res);
        setShowShiftBanner(true);
      } else {
        setShowShiftBanner(false);
      }
    } catch (err) {
      console.error('Failed to check domain shift:', err);
    }
  };

  // Start / stop stream listener
  useEffect(() => {
    if (!isStreaming) {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      return;
    }

    const streamUrl = api.getStreamUrl(
      selectedDomain,
      selectedModels.join(','),
      speed,
      seed
    );

    const es = new EventSource(streamUrl);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const payload: StreamFlowEvent = JSON.parse(event.data);
        setFlowHistory((prev) => [payload, ...prev.slice(0, 99)]); // keep last 100

        // Update running metrics per model
        setModelStats((prev) => {
          const next = { ...prev };
          const yTrue = payload.true_label;

          Object.entries(payload.predictions).forEach(([mName, pred]) => {
            if (!next[mName]) {
              next[mName] = { tp: 0, fp: 0, tn: 0, fn: 0 };
            }
            const yPred = pred.label;
            if (yTrue === 1 && yPred === 1) next[mName].tp += 1;
            if (yTrue === 0 && yPred === 1) next[mName].fp += 1;
            if (yTrue === 0 && yPred === 0) next[mName].tn += 1;
            if (yTrue === 1 && yPred === 0) next[mName].fn += 1;
          });

          return next;
        });
      } catch (e) {
        console.error('Error parsing SSE event:', e);
      }
    };

    es.onerror = () => {
      console.warn('SSE stream error or disconnected. Retrying...');
    };

    return () => {
      es.close();
    };
  }, [isStreaming, selectedDomain, selectedModels, speed, seed]);

  // Handle mid-stream domain switch
  const handleDomainChange = (newDomain: string) => {
    setSelectedDomain(newDomain);
    checkDomainShift(newDomain);
  };

  const toggleModelSelection = (mId: string) => {
    setSelectedModels((prev) =>
      prev.includes(mId)
        ? prev.filter((id) => id !== mId)
        : [...prev, mId]
    );
  };

  const handleReset = () => {
    setIsStreaming(false);
    setFlowHistory([]);
    setModelStats({});
    setShowShiftBanner(false);
  };

  // ECharts Timeline Configuration
  const chartOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      textStyle: { color: '#f8fafc', fontSize: 11, fontFamily: 'monospace' },
    },
    legend: {
      data: selectedModels,
      textStyle: { color: '#94a3b8', fontSize: 11 },
      top: 0,
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '40px', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [...flowHistory].reverse().map((f) => f.event_id),
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#64748b', fontSize: 10, fontFamily: 'monospace' },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 1,
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#64748b', fontSize: 10, fontFamily: 'monospace' },
    },
    series: selectedModels.map((mId) => ({
      name: mId,
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: [...flowHistory]
        .reverse()
        .map((f) => f.predictions[mId]?.probability ?? 0),
    })),
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100 font-mono flex items-center gap-2">
            <Activity className="w-6 h-6 text-cyan-400" />
            <span>Live Telemetry Stream & Real-Time Evaluator</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time flow ingestion, balanced accuracy / specificity tracking, and active domain shift alerting.
          </p>
        </div>

        <ProvenanceBadge
          sourceFile="data/samples/nfton.parquet"
          protocolStatus="final"
        />
      </div>

      {/* Domain Shift Alert Banner */}
      {showShiftBanner && shiftAlert && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/40 text-amber-300 flex items-start gap-3 shadow-lg animate-in fade-in duration-200">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1 text-xs">
            <div className="font-bold font-mono text-slate-100 flex items-center gap-2">
              <span>⚠️ STATISTICAL DOMAIN SHIFT DETECTED MID-STREAM</span>
              <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono font-normal">
                Target: {shiftAlert.target_domain}
              </span>
            </div>
            <p className="text-amber-200/90 leading-relaxed">
              Target domain feature distribution diverges significantly from reference (KS threshold &gt; 0.10, PSI threshold &gt; 0.25). Unadapted models will experience performance degradation.
            </p>
          </div>
        </div>
      )}

      {/* Control Bar */}
      <Card className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
          {/* Domain Selector */}
          <div className="flex flex-wrap items-center gap-3">
            <label htmlFor="domain-select" className="text-xs font-semibold text-slate-300 font-mono">
              Domain:
            </label>
            <select
              id="domain-select"
              value={selectedDomain}
              onChange={(e) => handleDomainChange(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
            >
              {domainOptions.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>

          {/* Model Selection Checkboxes */}
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs font-semibold text-slate-300 font-mono">
              Models:
            </span>
            {modelOptions.map((m) => (
              <label
                key={m.id}
                className="inline-flex items-center gap-1.5 text-xs font-mono text-slate-300 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedModels.includes(m.id)}
                  onChange={() => toggleModelSelection(m.id)}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-slate-900"
                />
                <span>{m.name}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Stream Action Controls */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsStreaming(!isStreaming)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg font-bold text-xs font-mono uppercase tracking-wider transition-all duration-150 focus:ring-2 focus:outline-none ${
                isStreaming
                  ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 focus:ring-amber-400'
                  : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 focus:ring-cyan-400 shadow-lg shadow-cyan-500/20'
              }`}
            >
              {isStreaming ? (
                <>
                  <Pause className="w-4 h-4" />
                  <span>Pause Stream</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Start Stream</span>
                </>
              )}
            </button>

            <button
              onClick={handleReset}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition-colors focus:ring-2 focus:ring-slate-500 focus:outline-none"
              title="Reset stream state"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
            {/* Speed Control */}
            <div className="flex items-center gap-2">
              <Sliders className="w-3.5 h-3.5 text-cyan-400" />
              <label htmlFor="speed-select">Speed:</label>
              <select
                id="speed-select"
                value={speed}
                onChange={(e) => setSpeed(Number(e.target.value))}
                className="px-2 py-1 rounded bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:ring-2 focus:ring-cyan-500 focus:outline-none"
              >
                <option value={1}>1x (1 flow/s)</option>
                <option value={5}>5x (5 flows/s)</option>
                <option value={10}>10x (10 flows/s)</option>
                <option value={20}>20x (20 flows/s)</option>
              </select>
            </div>

            {/* Seed Control */}
            <div className="flex items-center gap-2">
              <label htmlFor="seed-input">Seed:</label>
              <input
                id="seed-input"
                type="number"
                value={seed}
                onChange={(e) => setSeed(Number(e.target.value))}
                className="w-16 px-2 py-1 rounded bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:ring-2 focus:ring-cyan-500 focus:outline-none"
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Running Model Performance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {selectedModels.map((mId) => {
          const stats = modelStats[mId] || { tp: 0, fp: 0, tn: 0, fn: 0 };
          const recall =
            stats.tp + stats.fn > 0 ? stats.tp / (stats.tp + stats.fn) : 0;
          const specificity =
            stats.tn + stats.fp > 0 ? stats.tn / (stats.tn + stats.fp) : 0;
          const balancedAcc = (recall + specificity) / 2;

          return (
            <Card key={mId} className="space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-bold font-mono text-cyan-300 truncate max-w-[140px]" title={mId}>
                  {mId}
                </span>
                <ProvenanceBadge
                  sourceFile="results/verified/five_model_complete_comparison.csv"
                  protocolStatus="final"
                  compact
                />
              </div>

              <div className="space-y-2 font-mono text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Balanced Acc:</span>
                  <span className="text-emerald-400 font-extrabold text-sm">
                    {(balancedAcc * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Specificity (1-FPR):</span>
                  <span className="text-cyan-400 font-bold">
                    {(specificity * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Recall (TPR):</span>
                  <span className="text-blue-400 font-bold">
                    {(recall * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              <div className="text-[10px] font-mono text-slate-500 pt-2 border-t border-slate-800/60 flex justify-between">
                <span>TP: {stats.tp} | TN: {stats.tn}</span>
                <span>FP: {stats.fp} | FN: {stats.fn}</span>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Live Probability Timeline Chart */}
      <Card className="space-y-3">
        <h3 className="text-sm font-bold font-mono text-slate-100 flex items-center gap-2">
          <Clock className="w-4 h-4 text-cyan-400" />
          <span>Real-Time Model Threat Probability Output Timeline</span>
        </h3>
        <div className="h-64 w-full">
          <ReactECharts option={chartOption} style={{ height: '100%', width: '100%' }} />
        </div>
      </Card>

      {/* Stream Flow Table (Fixed Height to Prevent Layout Shift) */}
      <Card className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold font-mono text-slate-100">
            Streamed Flow Sequence (Last {flowHistory.length} Flows)
          </h3>
          <span className="text-xs font-mono text-slate-400">
            Fixed 320px scroll container (zero layout shift)
          </span>
        </div>

        <div className="h-[320px] overflow-y-auto rounded-lg border border-slate-800 bg-slate-950/80">
          <table className="w-full text-left font-mono text-xs text-slate-300">
            <thead className="sticky top-0 bg-slate-900 border-b border-slate-800 text-[11px] text-slate-400 uppercase">
              <tr>
                <th className="p-2.5">Flow ID</th>
                <th className="p-2.5">Domain</th>
                <th className="p-2.5">True Label</th>
                <th className="p-2.5">Packet Mean / Max</th>
                <th className="p-2.5">TCP Density</th>
                {selectedModels.map((m) => (
                  <th key={m} className="p-2.5">
                    {m}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-[11px]">
              {flowHistory.length === 0 ? (
                <tr>
                  <td colSpan={5 + selectedModels.length} className="p-8 text-center text-slate-500">
                    Click "Start Stream" above to begin real-time flow ingestion.
                  </td>
                </tr>
              ) : (
                flowHistory.map((flow) => (
                  <tr key={flow.event_id} className="hover:bg-slate-900/50">
                    <td className="p-2.5 font-bold text-cyan-400">{flow.event_id}</td>
                    <td className="p-2.5 text-slate-400">{flow.domain}</td>
                    <td className="p-2.5">
                      {flow.true_label === 1 ? (
                        <span className="inline-flex items-center gap-1 text-rose-400 font-bold">
                          <XCircle className="w-3 h-3" /> ATTACK
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-emerald-400 font-bold">
                          <CheckCircle2 className="w-3 h-3" /> BENIGN
                        </span>
                      )}
                    </td>
                    <td className="p-2.5">{flow.features.pkt_mean_to_max?.toFixed(4)}</td>
                    <td className="p-2.5">{flow.features.tcp_flag_density?.toFixed(4)}</td>
                    {selectedModels.map((m) => {
                      const pred = flow.predictions[m];
                      const prob = pred?.probability ?? 0;
                      return (
                        <td key={m} className="p-2.5">
                          <span
                            className={`px-1.5 py-0.5 rounded font-bold ${
                              prob >= 0.5 ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
                            }`}
                          >
                            {(prob * 100).toFixed(1)}%
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
