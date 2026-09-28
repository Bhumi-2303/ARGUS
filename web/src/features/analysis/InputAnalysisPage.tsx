import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Play,
  Database,
  ShieldAlert,
  CheckCircle,
  Upload,
  ArrowRight,
  Search,
  Cpu,
  Layers,
  FileText,
  AlertTriangle,
  RotateCcw,
  Activity,
} from 'lucide-react';

import { api, PredictRequest, PredictResponse, TestCaseItem, SampleItem } from '../../api/client';
import { Card } from '../../components/Card';
import { StatusPill } from '../../components/StatusPill';
import { ProvenanceBadge } from '../../components/ProvenanceBadge';

export default function InputAnalysisPage() {
  const [activeTab, setActiveTab] = useState<'single' | 'test-cases'>('single');
  const [selectedSample, setSelectedSample] = useState<SampleItem | TestCaseItem | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('model_d2_coral');
  const [customFeatures, setCustomFeatures] = useState<{
    pkt_mean_to_max: number;
    tcp_flag_density: number;
    log_pkt_mean: number;
    log_pkt_max: number;
  } | null>(null);
  const [csvFileName, setCsvFileName] = useState<string>('');
  const [uploadError, setUploadError] = useState<string>('');

  const [demoState, setDemoState] = useState<'IDLE' | 'PROCESSING' | 'RESULT_READY' | 'ERROR'>('IDLE');
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch real samples and verified test cases
  const { data: samples, isLoading: loadingSamples } = useQuery({
    queryKey: ['samples'],
    queryFn: () => api.getSamples(),
  });

  const { data: testCases, isLoading: loadingTestCases } = useQuery({
    queryKey: ['test_cases'],
    queryFn: () => api.getTestCases(),
  });

  // Multi-test-cases live execution state
  const [testCaseResults, setTestCaseResults] = useState<
    Record<string, { coral: PredictResponse | null; source: PredictResponse | null; loading: boolean }>
  >({});

  const predictMutation = useMutation({
    mutationFn: (req: PredictRequest) => api.predict(req),
    onSuccess: (data) => {
      setResult(data);
      setDemoState('RESULT_READY');
    },
    onError: (err: any) => {
      setErrorMsg(err.message || 'Error executing live model inference');
      setDemoState('ERROR');
    },
  });

  const flowMutation = useMutation({
    mutationFn: (req: PredictRequest) => api.simulateFlow(),
  });

  const handleSelectSample = (sample: SampleItem | TestCaseItem) => {
    setSelectedSample(sample);
    setCustomFeatures(sample.features);
    setCsvFileName('');
    setUploadError('');
    localStorage.setItem('argus_active_sample', JSON.stringify(sample));
    setDemoState('IDLE');
    setResult(null);
    setErrorMsg('');
  };

  const handleCsvUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setCsvFileName(file.name);
    setUploadError('');

    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const text = evt.target?.result as string;
        const lines = text.trim().split('\n');
        if (lines.length < 2) {
          throw new Error('CSV file must contain a header line and at least one data row.');
        }

        const headers = lines[0].split(',').map((h) => h.trim().replace(/['"]/g, ''));
        const row = lines[1].split(',').map((v) => v.trim());

        const getCol = (name: string): number => {
          const idx = headers.indexOf(name);
          if (idx === -1) {
            throw new Error(`Missing required harmonized feature column: '${name}'`);
          }
          const val = parseFloat(row[idx]);
          if (isNaN(val)) {
            throw new Error(`Invalid numeric value in column '${name}': '${row[idx]}'`);
          }
          return val;
        };

        const parsed = {
          pkt_mean_to_max: getCol('pkt_mean_to_max'),
          tcp_flag_density: getCol('tcp_flag_density'),
          log_pkt_mean: getCol('log_pkt_mean'),
          log_pkt_max: getCol('log_pkt_max'),
        };

        setCustomFeatures(parsed);
        setSelectedSample({
          id: `upload-${file.name}`,
          description: `Custom CSV Upload: ${file.name}`,
          domain: 'custom',
          ground_truth_label: -1,
          ground_truth_class: 'User Upload',
          features: parsed,
        });
        localStorage.setItem(
          'argus_active_sample',
          JSON.stringify({
            id: `upload-${file.name}`,
            description: `Custom CSV Upload: ${file.name}`,
            features: parsed,
          })
        );
        setDemoState('IDLE');
        setResult(null);
      } catch (err: any) {
        setUploadError(err.message || 'Failed to parse CSV file.');
      }
    };
    reader.readAsText(file);
  };

  const handleRunAnalysis = () => {
    if (!customFeatures) return;
    setDemoState('PROCESSING');
    setErrorMsg('');

    const req: PredictRequest = {
      model_name: selectedModel,
      features: customFeatures,
    };

    predictMutation.mutate(req);
    flowMutation.mutate(req);
  };

  const handleRunAllTestCases = async () => {
    if (!testCases || testCases.length === 0) return;

    const initialMap: Record<string, { coral: PredictResponse | null; source: PredictResponse | null; loading: boolean }> = {};
    testCases.forEach((tc) => {
      initialMap[tc.id] = { coral: null, source: null, loading: true };
    });
    setTestCaseResults(initialMap);

    for (const tc of testCases) {
      try {
        const [coralRes, sourceRes] = await Promise.all([
          api.predict({ model_name: 'xgb_adapted', features: tc.features }),
          api.predict({ model_name: 'xgb_source', features: tc.features }),
        ]);

        setTestCaseResults((prev) => ({
          ...prev,
          [tc.id]: { coral: coralRes, source: sourceRes, loading: false },
        }));
      } catch (e) {
        setTestCaseResults((prev) => ({
          ...prev,
          [tc.id]: { coral: null, source: null, loading: false },
        }));
      }
    }
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100 font-mono flex items-center gap-2">
            <Database className="w-6 h-6 text-cyan-400" />
            <span>Telemetry Input & Live Pipeline Inference</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Input genuine network telemetry flows, execute live multi-agent inference, and observe cross-domain behavior.
          </p>
        </div>

        <ProvenanceBadge
          sourceFile="results/verified/five_model_complete_comparison.csv"
          protocolStatus="final"
        />
      </div>

      {/* Tabs for Navigation */}
      <div className="flex border-b border-slate-800 text-xs font-mono">
        <button
          onClick={() => setActiveTab('single')}
          className={`px-4 py-2 font-bold border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'single'
              ? 'border-cyan-500 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Database className="w-4 h-4" />
          <span>Single Telemetry Flow Analysis</span>
        </button>
        <button
          onClick={() => setActiveTab('test-cases')}
          className={`px-4 py-2 font-bold border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'test-cases'
              ? 'border-cyan-500 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Multiple Test Cases (4 Verified Rows)</span>
        </button>
      </div>

      {activeTab === 'single' ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Input Selection & CSV Upload */}
          <Card className="space-y-4">
            <h2 className="text-sm font-bold font-mono text-slate-100 border-b border-slate-800 pb-2 flex items-center gap-2">
              <Database className="w-4 h-4 text-cyan-400" />
              <span>Step 2: Select or Upload Input Telemetry</span>
            </h2>

            {/* CSV File Upload Section */}
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold text-slate-300 flex items-center gap-1.5">
                  <Upload className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Upload Custom CSV Telemetry</span>
                </span>
                <span className="text-[10px] font-mono text-slate-400">4 Harmonized Features</span>
              </div>
              <input
                type="file"
                accept=".csv"
                onChange={handleCsvUpload}
                className="w-full text-xs font-mono text-slate-400 file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-mono file:bg-cyan-500/20 file:text-cyan-300 hover:file:bg-cyan-500/30 cursor-pointer"
              />
              {csvFileName && (
                <div className="text-[11px] font-mono text-emerald-400 flex items-center gap-1 mt-1">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Loaded: {csvFileName}</span>
                </div>
              )}
              {uploadError && (
                <div className="text-[11px] font-mono text-rose-400 flex items-center gap-1 mt-1">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>{uploadError}</span>
                </div>
              )}
            </div>

            {/* Real Samples from Dataset */}
            <div className="space-y-2">
              <div className="text-xs font-mono font-semibold text-slate-300 flex items-center justify-between">
                <span>Or Select from Verified Test Samples:</span>
                <span className="text-[10px] text-slate-400">ciciot / nfton parquets</span>
              </div>

              {loadingSamples ? (
                <div className="p-4 text-center text-xs text-slate-400 font-mono">Loading verified samples...</div>
              ) : !samples || samples.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-400 font-mono">No samples discovered.</div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {samples.map((s) => {
                    const isSelected = selectedSample?.id === s.id;
                    return (
                      <button
                        key={s.id}
                        type="button"
                        onClick={() => handleSelectSample(s)}
                        className={`text-left p-3 rounded-lg border text-xs font-mono transition-all ${
                          isSelected
                            ? 'border-cyan-500 bg-cyan-950/30 text-cyan-200'
                            : 'border-slate-800 bg-slate-950/40 text-slate-300 hover:border-slate-700'
                        }`}
                      >
                        <div className="font-bold flex items-center justify-between">
                          <span>{s.description}</span>
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] ${
                              s.ground_truth_label === 1
                                ? 'bg-rose-500/20 text-rose-300'
                                : 'bg-emerald-500/20 text-emerald-300'
                            }`}
                          >
                            {s.ground_truth_class}
                          </span>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-1">Domain: {s.domain.toUpperCase()}</div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Model Selector */}
            <div className="space-y-1.5 pt-2 border-t border-slate-800">
              <label htmlFor="model-select" className="text-xs font-mono font-semibold text-slate-300 block">
                Model for Live Inference:
              </label>
              <select
                id="model-select"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
              >
                <option value="xgb_adapted">Clean Class-Aware CORAL (XGBoost, D2 Target Aligned, Thresh 0.99)</option>
                <option value="model_d2_coral">LightGBM D2 CORAL (Legacy Booster, Thresh 0.85)</option>
                <option value="xgb_source">XGBoost Source-Only (Unadapted Baseline, Thresh 0.50)</option>
                <option value="model_d1_baseline">LightGBM D1 Baseline (Source Trained, Thresh 0.50)</option>
                <option value="dann" disabled>
                  DANN Neural Net (No verified checkpoint — unavailable for live inference)
                </option>
              </select>
            </div>

            {/* Features Inspector */}
            {customFeatures && (
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 font-mono text-xs space-y-1">
                <div className="text-slate-400 text-[10px] uppercase font-bold">Input Feature Vector:</div>
                <div className="grid grid-cols-2 gap-2 text-[11px] pt-1">
                  <div>
                    <span className="text-slate-400">pkt_mean_to_max: </span>
                    <span className="text-cyan-300 font-bold">{customFeatures.pkt_mean_to_max.toFixed(4)}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">tcp_flag_density: </span>
                    <span className="text-cyan-300 font-bold">{customFeatures.tcp_flag_density.toFixed(4)}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">log_pkt_mean: </span>
                    <span className="text-cyan-300 font-bold">{customFeatures.log_pkt_mean.toFixed(4)}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">log_pkt_max: </span>
                    <span className="text-cyan-300 font-bold">{customFeatures.log_pkt_max.toFixed(4)}</span>
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={handleRunAnalysis}
              disabled={!customFeatures || demoState === 'PROCESSING'}
              className="w-full mt-4 flex items-center justify-center gap-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-bold font-mono py-2.5 px-4 rounded-xl transition-all shadow-lg shadow-cyan-500/20"
            >
              <Play className="w-4 h-4" />
              <span>{demoState === 'PROCESSING' ? 'Executing Multi-Agent Pipeline...' : 'Run Live Inference'}</span>
            </button>
          </Card>

          {/* Right Column: Prediction Result (Step 4) */}
          <Card className="space-y-4 border-t-4 border-t-cyan-500 flex flex-col justify-between">
            <div className="space-y-4">
              <h2 className="text-sm font-bold font-mono text-slate-100 border-b border-slate-800 pb-2 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-cyan-400" />
                <span>Step 4: Live Prediction Outcome</span>
              </h2>

              {demoState === 'ERROR' && (
                <div className="p-4 rounded-lg bg-rose-950/40 border border-rose-800 text-rose-300 text-xs font-mono space-y-1">
                  <div className="font-bold flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Inference Execution Error</span>
                  </div>
                  <p>{errorMsg}</p>
                </div>
              )}

              {demoState === 'RESULT_READY' && result && (
                <div className="space-y-6 pt-2 font-mono">
                  {/* Verdict Badge */}
                  <div className="flex justify-between items-center bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <span className="text-xs font-bold text-slate-400 uppercase">Binary Classification Verdict</span>
                    <StatusPill
                      status={result.prediction === 1 ? 'error' : 'healthy'}
                      label={result.prediction === 1 ? 'ATTACK DETECTED' : 'BENIGN TRAFFIC'}
                    />
                  </div>

                  {/* Confidence Bar */}
                  <div className="space-y-2 p-4 rounded-xl bg-slate-950 border border-slate-800">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-400">Attack Probability:</span>
                      <span className="font-bold text-cyan-300">{(result.probability * 100).toFixed(2)}%</span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
                      <div
                        className={`h-full transition-all duration-500 ${
                          result.prediction === 1 ? 'bg-rose-500' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${Math.min(100, Math.max(0, result.probability * 100))}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-[10px] text-slate-400 pt-1">
                      <span>0.00 (Benign)</span>
                      <span>Threshold: {result.threshold}</span>
                      <span>1.00 (Attack)</span>
                    </div>
                  </div>

                  {/* Metadata Audit Box */}
                  <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs space-y-1.5">
                    <div className="text-[10px] font-bold text-slate-400 uppercase">Inference Details:</div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Evaluated Model:</span>
                      <span className="text-cyan-300 font-bold">{result.model_name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Decision Threshold:</span>
                      <span className="text-slate-200 font-bold">{result.threshold}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Raw Model Probability:</span>
                      <span className="text-slate-200 font-bold">{result.probability.toFixed(6)}</span>
                    </div>
                  </div>
                </div>
              )}

              {demoState !== 'RESULT_READY' && demoState !== 'ERROR' && (
                <div className="h-48 flex flex-col items-center justify-center text-xs font-mono text-slate-400 space-y-2">
                  <Activity className="w-8 h-8 text-slate-700 animate-pulse" />
                  <span>
                    {demoState === 'PROCESSING'
                      ? 'Executing model inference and dispatching agent trace...'
                      : 'Select a telemetry row and click "Run Live Inference"'}
                  </span>
                </div>
              )}
            </div>

            {/* Quick Links to Explanations & Topology */}
            {demoState === 'RESULT_READY' && (
              <div className="pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2 font-mono text-xs">
                <Link
                  to="/explain"
                  className="inline-flex items-center gap-1.5 text-cyan-400 hover:text-cyan-300 font-semibold"
                >
                  <Search className="w-3.5 h-3.5" />
                  <span>Inspect SHAP Attribution</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
                <Link
                  to="/topology"
                  className="inline-flex items-center gap-1.5 text-purple-400 hover:text-purple-300 font-semibold"
                >
                  <Cpu className="w-3.5 h-3.5" />
                  <span>Trace Agent Orchestration</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            )}
          </Card>
        </div>
      ) : (
        /* Tab 2: Multiple Test Cases (Step 6) */
        <Card className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-base font-bold font-mono text-slate-100 flex items-center gap-2">
                <Layers className="w-5 h-5 text-cyan-400" />
                <span>Step 6: Four Verified Benchmark Test Cases</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Real binary-labeled flows from CICIoT2023 (Source) and NF-ToN-IoT-v2 (Target) evaluated live across Clean CORAL and unadapted XGBoost.
              </p>
              <p className="text-[11px] text-slate-400 mt-1 font-mono">
                <span className="text-cyan-400 font-semibold">Selection Rule:</span> First benign and first attack row of each test CSV (<code>ciciot_test_features.csv</code> for D1, <code>nfton_test_features.csv</code> for D2).
              </p>
            </div>

            <button
              onClick={handleRunAllTestCases}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold font-mono text-xs uppercase tracking-wider transition-colors shadow-lg shadow-cyan-500/20"
            >
              <Play className="w-4 h-4" />
              <span>Run All 4 Cases Live</span>
            </button>
          </div>

          {loadingTestCases ? (
            <div className="p-8 text-center text-xs font-mono text-slate-400">Loading test cases...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {testCases?.map((tc) => {
                const res = testCaseResults[tc.id];
                const coralProb = res?.coral?.probability;
                const coralPred = res?.coral?.prediction;
                const sourceProb = res?.source?.probability;
                const sourcePred = res?.source?.prediction;

                return (
                  <div
                    key={tc.id}
                    className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-3 font-mono text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-200">{tc.name}</span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          tc.ground_truth_label === 1
                            ? 'bg-rose-500/20 text-rose-300'
                            : 'bg-emerald-500/20 text-emerald-300'
                        }`}
                      >
                        Ground Truth: {tc.ground_truth_class}
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-400">{tc.provenance}</div>

                    {/* Features breakdown */}
                    <div className="grid grid-cols-2 gap-1.5 p-2.5 rounded bg-slate-900/80 border border-slate-800 text-[11px]">
                      <div>pkt_mean_to_max: <span className="text-cyan-300">{tc.features.pkt_mean_to_max.toFixed(4)}</span></div>
                      <div>tcp_flag_density: <span className="text-cyan-300">{tc.features.tcp_flag_density.toFixed(4)}</span></div>
                      <div>log_pkt_mean: <span className="text-cyan-300">{tc.features.log_pkt_mean.toFixed(4)}</span></div>
                      <div>log_pkt_max: <span className="text-cyan-300">{tc.features.log_pkt_max.toFixed(4)}</span></div>
                    </div>

                    {/* Live Results & Verified Population comparison */}
                    <div className="space-y-2 pt-2 border-t border-slate-800/80">
                      <div className="text-[10px] uppercase font-bold text-slate-400">Live Model Predictions & Population Context:</div>

                      {/* Clean CORAL Live + Verified Population */}
                      <div className="p-2.5 rounded bg-slate-900 border border-slate-800 space-y-1.5">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-slate-300 font-bold block">Clean Class-Aware CORAL (XGBoost, D2 Aligned):</span>
                            <span className="text-[10px] text-slate-400">Calibrated Threshold: 0.99</span>
                          </div>
                          {res?.loading ? (
                            <span className="text-cyan-400 text-xs animate-pulse">Running...</span>
                          ) : coralPred !== undefined ? (
                            <div className="text-right">
                              <span
                                className={`font-bold ${
                                  coralPred === tc.ground_truth_label ? 'text-emerald-400' : 'text-amber-400'
                                }`}
                              >
                                {coralPred === 1 ? 'ATTACK' : 'BENIGN'} ({((coralProb || 0) * 100).toFixed(1)}%)
                              </span>
                              <span className="text-[10px] block text-slate-400">
                                {coralPred === tc.ground_truth_label ? 'Correct' : 'Shift Error'}
                              </span>
                            </div>
                          ) : (
                            <span className="text-slate-400 text-xs">Awaiting execution</span>
                          )}
                        </div>
                        {/* Verified Population Metrics Badge */}
                        <div className="pt-1.5 border-t border-slate-800/60 flex flex-wrap items-center justify-between text-[10px] text-slate-400">
                          <span className="text-cyan-400 font-semibold">Population (Clean CORAL XGBoost, N=2.62M):</span>
                          <span>MCC: <strong className="text-slate-200">0.3855</strong></span>
                          <span>Prec: <strong className="text-slate-200">94.00%</strong></span>
                          <span>Spec: <strong className="text-slate-200">91.43%</strong></span>
                        </div>
                      </div>

                      {/* Source-Only XGBoost Live + Verified Population */}
                      <div className="p-2.5 rounded bg-slate-900 border border-slate-800 space-y-1.5">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-slate-300 font-bold block">Source-Only XGBoost:</span>
                            <span className="text-[10px] text-slate-400">Threshold: 0.50</span>
                          </div>
                          {res?.loading ? (
                            <span className="text-cyan-400 text-xs animate-pulse">Running...</span>
                          ) : sourcePred !== undefined ? (
                            <div className="text-right">
                              <span
                                className={`font-bold ${
                                  sourcePred === tc.ground_truth_label ? 'text-emerald-400' : 'text-rose-400'
                                }`}
                              >
                                {sourcePred === 1 ? 'ATTACK' : 'BENIGN'} ({((sourceProb || 0) * 100).toFixed(1)}%)
                              </span>
                              <span className="text-[10px] block text-slate-400">
                                {sourcePred === tc.ground_truth_label ? 'Correct' : 'False Positive on Target'}
                              </span>
                            </div>
                          ) : (
                            <span className="text-slate-400 text-xs">Awaiting execution</span>
                          )}
                        </div>
                        {/* Verified Population Metrics Badge */}
                        <div className="pt-1.5 border-t border-slate-800/60 flex flex-wrap items-center justify-between text-[10px] text-slate-400">
                          <span className="text-amber-400 font-semibold">Population (Source-Only XGBoost, N=2.62M):</span>
                          <span>MCC: <strong className="text-slate-200">-0.0311</strong></span>
                          <span>Prec: <strong className="text-slate-200">72.47%</strong></span>
                          <span>Spec: <strong className="text-rose-400">0.25%</strong></span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

