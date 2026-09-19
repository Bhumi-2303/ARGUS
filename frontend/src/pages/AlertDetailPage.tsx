import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import {
  ArrowLeft,
  ShieldAlert,
  AlertOctagon,
  CheckCircle2,
  Clock,
  Cpu,
  Layers,
  Sparkles,
  BarChart3,
  FileText,
  Play,
  X,
  Check
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';

import { Alert, Explanation, ModelMetrics, AuditEvent } from '../types';
import {
  getAlertById,
  getExplanationByAlertId,
  getModels,
  getAuditEvents
} from '../services/api';

type TabType = 'overview' | 'explanation' | 'risk' | 'response' | 'logs';

export const AlertDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // Tab State synced with URL query param `?tab=...`
  const currentTab = (searchParams.get('tab') as TabType) || 'overview';

  const setTab = (tab: TabType) => {
    setSearchParams({ tab });
  };

  const [alert, setAlert] = useState<Alert | null>(null);
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [modelsList, setModelsList] = useState<ModelMetrics[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Response Confirmation Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [actionStatus, setActionStatus] = useState<'idle' | 'executing' | 'completed'>('idle');

  useEffect(() => {
    let mounted = true;
    async function loadData() {
      if (!id) return;
      try {
        const [fetchedAlert, fetchedExp, fetchedModels, fetchedEvents] = await Promise.all([
          getAlertById(id),
          getExplanationByAlertId(id),
          getModels(),
          getAuditEvents()
        ]);

        if (mounted) {
          setAlert(fetchedAlert || null);
          setExplanation(fetchedExp || null);
          setModelsList(fetchedModels);
          setAuditLogs(fetchedEvents);
          setLoading(false);
        }
      } catch (err) {
        console.error('Failed to load alert details:', err);
        if (mounted) setLoading(false);
      }
    }
    loadData();

    return () => {
      mounted = false;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="p-12 text-center text-text-secondary font-mono text-xs flex flex-col items-center justify-center gap-3">
        <div className="w-6 h-6 border-2 border-info border-t-transparent rounded-full animate-spin" />
        <span>Fetching incident telemetry for {id}...</span>
      </div>
    );
  }

  if (!alert) {
    return (
      <div className="p-12 glass-panel text-center text-text-secondary space-y-4">
        <AlertOctagon className="w-10 h-10 text-critical mx-auto" />
        <h2 className="text-lg font-bold text-text-primary">Alert Not Found</h2>
        <p className="text-xs font-mono">The requested alert ID ({id}) could not be located in the SOC incident queue.</p>
        <button
          onClick={() => navigate('/alerts')}
          className="px-4 py-2 rounded-lg bg-info/10 border border-info/30 text-info text-xs font-mono hover:bg-info/20 transition-colors inline-flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Alerts Queue</span>
        </button>
      </div>
    );
  }

  const isCritical = alert.severity === 'critical';

  // Sub-scores for Risk Analysis Radar/Bar
  const riskBreakdownData = [
    { subject: 'Threat Severity', score: Math.min(100, alert.riskScore + 2), fullMark: 100 },
    { subject: 'Asset Criticality', score: Math.min(100, Math.round(alert.riskScore * 0.95)), fullMark: 100 },
    { subject: 'Blast Radius', score: Math.min(100, Math.round(alert.riskScore * 0.85)), fullMark: 100 },
    { subject: 'Vulnerability Index', score: Math.min(100, Math.round(alert.riskScore * 0.90)), fullMark: 100 }
  ];

  const handleSimulatedAction = () => {
    setActionStatus('executing');
    setTimeout(() => {
      setActionStatus('completed');
      setAlert((prev) => (prev ? { ...prev, status: 'contained' } : prev));
      setTimeout(() => {
        setIsModalOpen(false);
        setActionStatus('idle');
      }, 1500);
    }, 1200);
  };

  return (
    <div className="space-y-6 select-none">
      {/* Top Back Navigation Bar */}
      <div>
        <button
          onClick={() => navigate('/alerts')}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-bg-surface border border-border-muted text-xs font-mono text-text-secondary hover:text-text-primary hover:border-info/40 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Alerts Queue</span>
        </button>
      </div>

      {/* Header Banner (Styled as Red Critical Banner if severity is critical) */}
      <div
        className={`p-6 rounded-xl border transition-all ${
          isCritical
            ? 'bg-critical/15 border-critical/40 glow-critical shadow-2xl'
            : 'glass-panel-raised border-border-muted'
        }`}
      >
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          {/* Main Threat Metadata */}
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={`px-3 py-1 rounded-full text-xs font-mono font-bold uppercase tracking-wider border ${
                  isCritical
                    ? 'bg-critical text-text-primary border-critical glow-critical'
                    : 'bg-warn/20 text-warn border-warn/40'
                }`}
              >
                {alert.severity} THREAT INCIDENT
              </span>

              <span className="px-2.5 py-0.5 rounded bg-bg-surface-raised border border-border-muted text-xs font-mono text-text-secondary">
                {alert.id}
              </span>

              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold uppercase border ${
                  alert.status === 'active'
                    ? 'bg-critical/20 text-critical border-critical/40'
                    : alert.status === 'contained'
                    ? 'bg-info/20 text-info border-info/40'
                    : 'bg-safe/20 text-safe border-safe/40'
                }`}
              >
                {alert.status}
              </span>
            </div>

            <h1 className="text-2xl font-bold text-text-primary tracking-tight">
              {alert.attackType}
            </h1>

            <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-text-secondary">
              <div>
                <span className="opacity-70">SOURCE:</span>{' '}
                <span className="text-text-primary font-semibold">{alert.source}</span>
              </div>
              <span>→</span>
              <div>
                <span className="opacity-70">TARGET:</span>{' '}
                <span className="text-text-primary font-semibold">{alert.target}</span>
              </div>
            </div>
          </div>

          {/* Right Metrics Cards */}
          <div className="flex items-center gap-4 self-start lg:self-center">
            {/* Confidence Score */}
            <div className="p-3 rounded-lg bg-bg-surface/80 border border-border-muted text-center min-w-[100px]">
              <span className="text-[10px] font-mono text-text-secondary uppercase block">CONFIDENCE</span>
              <span className="text-xl font-bold font-mono text-info mt-0.5 block">
                {(alert.confidence * 100).toFixed(0)}%
              </span>
            </div>

            {/* Risk Score */}
            <div className="p-3 rounded-lg bg-bg-surface/80 border border-border-muted text-center min-w-[100px]">
              <span className="text-[10px] font-mono text-text-secondary uppercase block">RISK SCORE</span>
              <span className={`text-xl font-bold font-mono mt-0.5 block ${alert.riskScore > 75 ? 'text-critical' : 'text-warn'}`}>
                {alert.riskScore}/100
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="flex border-b border-border-muted overflow-x-auto">
        <button
          onClick={() => setTab('overview')}
          className={`flex items-center gap-2 px-5 py-3 text-xs font-mono font-semibold transition-all border-b-2 whitespace-nowrap ${
            currentTab === 'overview'
              ? 'border-info text-info bg-info/5'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Overview</span>
        </button>

        <button
          onClick={() => setTab('explanation')}
          className={`flex items-center gap-2 px-5 py-3 text-xs font-mono font-semibold transition-all border-b-2 whitespace-nowrap ${
            currentTab === 'explanation'
              ? 'border-info text-info bg-info/5'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>Explanation (XAI)</span>
        </button>

        <button
          onClick={() => setTab('risk')}
          className={`flex items-center gap-2 px-5 py-3 text-xs font-mono font-semibold transition-all border-b-2 whitespace-nowrap ${
            currentTab === 'risk'
              ? 'border-info text-info bg-info/5'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Risk Analysis</span>
        </button>

        <button
          onClick={() => setTab('response')}
          className={`flex items-center gap-2 px-5 py-3 text-xs font-mono font-semibold transition-all border-b-2 whitespace-nowrap ${
            currentTab === 'response'
              ? 'border-info text-info bg-info/5'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          }`}
        >
          <Play className="w-4 h-4" />
          <span>Response & Action</span>
        </button>

        <button
          onClick={() => setTab('logs')}
          className={`flex items-center gap-2 px-5 py-3 text-xs font-mono font-semibold transition-all border-b-2 whitespace-nowrap ${
            currentTab === 'logs'
              ? 'border-info text-info bg-info/5'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Logs & Audit</span>
        </button>
      </div>

      {/* Tab 1: Overview */}
      {currentTab === 'overview' && (
        <div className="space-y-6">
          {/* Section: Model Detection Evidence */}
          <div>
            <h3 className="text-sm font-mono font-bold tracking-wider text-text-secondary uppercase mb-3 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-info" /> MULTI-MODEL DETECTION EVIDENCE
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {modelsList.map((model) => {
                const isWinner = model.name === 'LightGBM';
                return (
                  <div key={model.name} className="glass-panel p-5 space-y-4 relative overflow-hidden">
                    {isWinner && (
                      <span className="absolute top-3 right-3 text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-info/20 text-info border border-info/30 uppercase">
                        PRIMARY DETECTOR
                      </span>
                    )}

                    <div>
                      <h4 className="text-base font-bold text-text-primary">{model.name}</h4>
                      <p className="text-[10px] text-text-secondary font-mono mt-0.5">
                        Prototype model inference prediction
                      </p>
                    </div>

                    {/* Confidence Progress Bar */}
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs font-mono">
                        <span className="text-text-secondary">Model Confidence:</span>
                        <span className="font-bold text-info">{(model.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-bg-surface-raised overflow-hidden">
                        <div
                          className="h-full bg-info"
                          style={{ width: `${model.confidence * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-bg-surface p-3 rounded-lg border border-border-muted/60">
                      <div>
                        <span className="text-text-secondary block text-[10px]">ACCURACY</span>
                        <span className="font-bold text-text-primary">{(model.accuracy * 100).toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-text-secondary block text-[10px]">PRECISION</span>
                        <span className="font-bold text-text-primary">{(model.precision * 100).toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-text-secondary block text-[10px]">RECALL</span>
                        <span className="font-bold text-text-primary">{(model.recall * 100).toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-text-secondary block text-[10px]">MCC SCORE</span>
                        <span className="font-bold text-text-primary">{model.mcc.toFixed(3)}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section: ARGUS Decision Chain Stepper */}
          <div className="glass-panel p-6 space-y-4">
            <h3 className="text-sm font-mono font-bold tracking-wider text-text-secondary uppercase flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-safe" /> ARGUS DECISION CHAIN PIPELINE
            </h3>

            <div className="space-y-3 font-mono text-xs">
              {/* Step 1 */}
              <div className="flex items-start gap-3 p-3 rounded-lg bg-safe/10 border border-safe/30 text-safe">
                <CheckCircle2 className="w-4 h-4 text-safe mt-0.5 flex-shrink-0" />
                <div>
                  <span className="font-bold uppercase tracking-wider block">STEP 1: DETECTION COMPLETED</span>
                  <span className="text-text-secondary text-[11px] block mt-0.5">
                    Flow telemetry extracted & classified across LightGBM, XGBoost, and FT-Transformer models.
                  </span>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex items-start gap-3 p-3 rounded-lg bg-safe/10 border border-safe/30 text-safe">
                <CheckCircle2 className="w-4 h-4 text-safe mt-0.5 flex-shrink-0" />
                <div>
                  <span className="font-bold uppercase tracking-wider block">STEP 2: RISK ASSESSMENT COMPLETED</span>
                  <span className="text-text-secondary text-[11px] block mt-0.5">
                    Grid topology asset criticality evaluated; risk score assigned ({alert.riskScore}/100).
                  </span>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex items-start gap-3 p-3 rounded-lg bg-safe/10 border border-safe/30 text-safe">
                <CheckCircle2 className="w-4 h-4 text-safe mt-0.5 flex-shrink-0" />
                <div>
                  <span className="font-bold uppercase tracking-wider block">STEP 3: EXPLAINABILITY GENERATED</span>
                  <span className="text-text-secondary text-[11px] block mt-0.5">
                    SHAP TreeExplainer feature attributions & MITRE ATT&CK vector search completed.
                  </span>
                </div>
              </div>

              {/* Step 4 */}
              <div className="flex items-start gap-3 p-3 rounded-lg bg-info/10 border border-info/30 text-info">
                <Play className="w-4 h-4 text-info mt-0.5 flex-shrink-0 animate-pulse" />
                <div>
                  <span className="font-bold uppercase tracking-wider block">STEP 4: RESPONSE AWAITING REVIEW</span>
                  <span className="text-text-secondary text-[11px] block mt-0.5">
                    Automated OpenFlow VLAN isolation policy ready for analyst review & execution.
                  </span>
                </div>
              </div>

              {/* Step 5 */}
              <div className="flex items-start gap-3 p-3 rounded-lg bg-bg-surface border border-border-muted text-text-secondary/60">
                <Clock className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="font-bold uppercase tracking-wider block">STEP 5: REPORTING PENDING</span>
                  <span className="text-text-secondary/60 text-[11px] block mt-0.5">
                    NERC-CIP compliance incident logging pending action resolution.
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Explanation (XAI) */}
      {currentTab === 'explanation' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 space-y-6">
            <div>
              <span className="text-[10px] font-mono text-text-secondary uppercase tracking-wider block">
                SHAP EXPLAINABILITY ENGINE ({explanation?.model || 'LightGBM'})
              </span>
              <h3 className="text-lg font-bold text-text-primary mt-1">
                Feature Contribution Breakdown
              </h3>
            </div>

            {/* SHAP Bar Chart */}
            {explanation ? (
              <div className="space-y-6">
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      layout="vertical"
                      data={explanation.features}
                      margin={{ top: 5, right: 30, left: 140, bottom: 5 }}
                    >
                      <XAxis type="number" stroke="#8b96a8" fontSize={11} />
                      <YAxis type="category" dataKey="feature" stroke="#8b96a8" fontSize={11} tick={{ fill: '#f2f5f9' }} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0a0e17', borderColor: '#1e2635', color: '#f2f5f9' }}
                        formatter={(value: number) => [`${value > 0 ? '+' : ''}${value.toFixed(2)}`, 'SHAP Value']}
                      />
                      <Bar dataKey="contribution">
                        {explanation.features.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={entry.contribution > 0 ? '#ef4444' : '#22c55e'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Narrative Explanation Box */}
                <div className="p-4 rounded-lg bg-bg-surface border border-info/30 glow-info space-y-2">
                  <div className="flex items-center gap-2 text-xs font-mono font-bold text-info uppercase">
                    <Sparkles className="w-4 h-4" /> HUMAN-READABLE XAI NARRATIVE
                  </div>
                  <p className="text-sm text-text-primary leading-relaxed font-sans">
                    "{explanation.narrative}"
                  </p>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-text-secondary font-mono text-xs">
                No detailed SHAP explanation entry found for this alert.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Risk Analysis */}
      {currentTab === 'risk' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Risk Breakdown Chart */}
            <div className="glass-panel p-6 space-y-4">
              <h3 className="text-sm font-mono font-bold tracking-wider text-text-secondary uppercase flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-info" /> RISK VECTOR BREAKDOWN
              </h3>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={riskBreakdownData}>
                    <PolarGrid stroke="#1e2635" />
                    <PolarAngleAxis dataKey="subject" stroke="#8b96a8" fontSize={11} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#8b96a8" fontSize={10} />
                    <Radar name="Risk Score" dataKey="score" stroke="#ef4444" fill="#ef4444" fillOpacity={0.4} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Impacted Asset Topology */}
            <div className="glass-panel p-6 space-y-4">
              <h3 className="text-sm font-mono font-bold tracking-wider text-text-secondary uppercase flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-warn" /> TOPOLOGICAL BLAST RADIUS
              </h3>

              <div className="space-y-3 font-mono text-xs">
                <div className="p-3 rounded-lg bg-bg-surface border border-border-muted flex justify-between items-center">
                  <span className="text-text-primary font-semibold">Primary Target: Substation North</span>
                  <span className="text-critical font-bold">CRITICAL IMPACT</span>
                </div>
                <div className="p-3 rounded-lg bg-bg-surface border border-border-muted flex justify-between items-center">
                  <span className="text-text-primary">Downstream RTU-01</span>
                  <span className="text-warn font-bold">HIGH EXPOSURE</span>
                </div>
                <div className="p-3 rounded-lg bg-bg-surface border border-border-muted flex justify-between items-center">
                  <span className="text-text-primary">Feeder Breaker Protection IED</span>
                  <span className="text-safe font-bold">PROTECTED</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Response & Action */}
      {currentTab === 'response' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-border-muted pb-4">
              <div>
                <span className="text-[10px] font-mono text-text-secondary uppercase tracking-wider block">
                  AUTOMATED PLAYBOOK RECOMMENDATION
                </span>
                <h3 className="text-xl font-bold text-text-primary mt-1">
                  ISOLATE SUBSTATION NORTH INGRESS PORT (TCP 2404)
                </h3>
              </div>
              <span className="px-3 py-1 rounded-full bg-critical/20 text-critical border border-critical/40 text-xs font-mono font-bold uppercase glow-critical">
                RECOMMENDED ACTION
              </span>
            </div>

            <p className="text-sm text-text-primary leading-relaxed">
              Automated containment policy recommendation based on high confidence ({(alert.confidence * 100).toFixed(0)}%) ASDU frame injection threat targeting primary substation relay interfaces. Isolating port 2404 prevents lateral command spooling across the 500kV feeder bus.
            </p>

            <div className="p-4 rounded-lg bg-bg-surface border border-border-muted space-y-2 font-mono text-xs">
              <div className="flex justify-between">
                <span className="text-text-secondary">TARGET ASSET:</span>
                <span className="text-text-primary font-bold">{alert.target}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">MITIGATION TYPE:</span>
                <span className="text-info font-bold">OPENFLOW VLAN ISOLATION</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">ESTIMATED DOWNTIME:</span>
                <span className="text-safe font-bold">0 SECONDS (FAIL-SAFE RE-ROUTE)</span>
              </div>
            </div>

            <div>
              <button
                onClick={() => setIsModalOpen(true)}
                className="px-6 py-3 rounded-lg bg-critical hover:bg-critical/90 text-text-primary font-mono font-bold text-sm shadow-lg glow-critical transition-all flex items-center gap-2"
              >
                <Play className="w-4 h-4 fill-current" />
                <span>Review Action</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Logs & Audit */}
      {currentTab === 'logs' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 space-y-4">
            <h3 className="text-sm font-mono font-bold tracking-wider text-text-secondary uppercase flex items-center gap-2">
              <FileText className="w-4 h-4 text-info" /> INCIDENT AUDIT STREAM
            </h3>

            <div className="space-y-2 font-mono text-xs">
              {auditLogs.map((log) => (
                <div key={log.id} className="p-3 rounded-lg bg-bg-surface border border-border-muted/60 flex items-start gap-3">
                  <span className="text-[10px] px-2 py-0.5 rounded bg-info/10 text-info border border-info/20 uppercase font-bold flex-shrink-0">
                    {log.agent}
                  </span>
                  <div className="flex-1">
                    <span className="text-text-primary">{log.message}</span>
                    <span className="text-[10px] text-text-secondary block mt-1">
                      {new Date(log.timestamp).toLocaleTimeString()} UTC
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-bg-void/80 backdrop-blur-md animate-in fade-in duration-150">
          <div className="w-full max-w-lg glass-panel-raised p-6 space-y-5 border border-critical/50 shadow-2xl glow-critical relative">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 p-1.5 rounded-lg bg-bg-surface text-text-secondary hover:text-text-primary"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-3 text-critical border-b border-border-muted pb-3">
              <AlertOctagon className="w-6 h-6 animate-pulse" />
              <h3 className="text-lg font-bold tracking-tight">CONFIRM MITIGATION ACTION</h3>
            </div>

            {/* Prototype Disclaimer Banner */}
            <div className="p-3 rounded-lg bg-critical/20 border border-critical/40 text-critical text-xs font-mono font-semibold">
              ⚠️ PROTOTYPE SOC ACTION RUNNER — This is a prototype system demonstration and will simulate action execution.
            </div>

            <div className="space-y-2 font-mono text-xs text-text-secondary">
              <p className="text-text-primary font-semibold">Action: ISOLATE SUBSTATION NORTH INGRESS PORT (TCP 2404)</p>
              <p>Target: {alert.target}</p>
              <p>Requested by: Operator-01 (SOC Analyst)</p>
            </div>

            {/* Modal Buttons */}
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-border-muted">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-bg-surface border border-border-muted text-xs font-mono text-text-secondary hover:text-text-primary"
                disabled={actionStatus === 'executing'}
              >
                Cancel
              </button>
              <button
                onClick={handleSimulatedAction}
                disabled={actionStatus === 'executing'}
                className="px-5 py-2 rounded-lg bg-critical text-text-primary font-mono font-bold text-xs glow-critical flex items-center gap-2 hover:bg-critical/90"
              >
                {actionStatus === 'executing' ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-text-primary border-t-transparent rounded-full animate-spin" />
                    <span>Executing Simulation...</span>
                  </>
                ) : actionStatus === 'completed' ? (
                  <>
                    <Check className="w-4 h-4 text-text-primary" />
                    <span>Action Executed!</span>
                  </>
                ) : (
                  <span>Execute Simulated Action</span>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertDetailPage;
