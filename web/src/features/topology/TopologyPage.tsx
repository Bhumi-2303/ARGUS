import React, { useState, useEffect, Suspense, useCallback, useMemo, lazy } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Activity,
  Play,
  Pause,
  RotateCcw,
  Layers,
  Info,
  CheckCircle2,
  AlertTriangle,
  Cpu,
  Network,
  GitBranch,
  Gauge,
  Sliders,
  ShieldCheck,
  Eye,
  BarChart3,
  Minimize2,
  Maximize2,
  Sparkles,
  Zap,
} from 'lucide-react';
import {
  api,
  TopologyNode,
  TopologyEdge,
  FlowEventItem,
  SimulateFlowResponse,
  ShiftPCAResponse,
} from '../../api/client';
import { ProvenanceBadge } from '../../components/ProvenanceBadge';
import { Card } from '../../components/Card';
import { Skeleton } from '../../components/Skeleton';
import { StatusPill } from '../../components/StatusPill';
import { TopologyGraph2D } from './TopologyGraph2D';
import { SceneMode, NodeState } from './TopologyCanvas3D';

// Lazy-load the heavy 3D chunk to keep initial bundle light
const TopologyCanvas3D = lazy(() => import('./TopologyCanvas3D'));

export type ViewMode =
  | '3D_TOPOLOGY'
  | '3D_DOMAIN_SHIFT'
  | '3D_SHAP'
  | '3D_DECISION_TIMELINE'
  | '2D';

export default function TopologyPage() {
  const queryClient = useQueryClient();
  const [viewMode, setViewMode] = useState<ViewMode>('3D_TOPOLOGY');
  const [selectedNode, setSelectedNode] = useState<TopologyNode | null>(null);
  const [activeCorrelationId, setActiveCorrelationId] = useState<string | null>(null);
  const [eventTrace, setEventTrace] = useState<FlowEventItem[]>([]);
  const [nodeEvents, setNodeEvents] = useState<Record<string, FlowEventItem[]>>({});
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [streamSpeed, setStreamSpeed] = useState<number>(5.0);
  const [selectedDomain, setSelectedDomain] = useState<'nfton' | 'ciciot'>('nfton');
  const [streamSeed, setStreamSeed] = useState<number>(42);

  // Performance & Accessibility Controls
  const [quality, setQuality] = useState<'high' | 'low'>('high');
  const [reducedMotion, setReducedMotion] = useState<boolean>(false);

  // Dynamic node runtime status mapping
  const [nodeStatusMap, setNodeStatusMap] = useState<Record<string, NodeState>>({
    DATA_INTELLIGENCE: 'idle',
    THREAT_ANALYSIS: 'idle',
    EXPLAINABILITY: 'idle',
    KNOWLEDGE_CONTEXT: 'idle',
    RISK_PREDICTION: 'idle',
    DECISION_SUPPORT: 'idle',
  });

  // Latest node telemetry detail
  const [nodeMetrics, setNodeMetrics] = useState<
    Record<string, { duration_ms?: number; input?: string; output?: string; error?: string }>
  >({});

  // Detect system prefers-reduced-motion
  useEffect(() => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      setReducedMotion(mediaQuery.matches);
      const listener = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
      mediaQuery.addEventListener('change', listener);
      return () => mediaQuery.removeEventListener('change', listener);
    }
  }, []);

  // Fetch Topology definition
  const { data: topologyData, isLoading: loadingTopology, refetch: refetchTopology } = useQuery({
    queryKey: ['agent_topology'],
    queryFn: api.getTopology,
  });

  // Fetch real 3D PCA point clouds and CORAL parameters
  const { data: shiftPCAData, isLoading: loadingShiftPCA } = useQuery({
    queryKey: ['shift_pca', selectedDomain],
    queryFn: () => api.getShiftPCA('ciciot', selectedDomain, 200, streamSeed),
    enabled: viewMode === '3D_DOMAIN_SHIFT',
  });

  // Fetch incidents for Decision Timeline and SHAP
  const { data: incidentsData } = useQuery({
    queryKey: ['incidents_list'],
    queryFn: api.getIncidents,
  });

  const incidentList = useMemo(() => {
    if (!incidentsData) return [];
    if (Array.isArray(incidentsData)) return incidentsData;
    if (incidentsData.data && Array.isArray(incidentsData.data)) return incidentsData.data;
    return [];
  }, [incidentsData]);

  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const selectedIncident = useMemo(() => {
    if (incidentList.length === 0) return null;
    if (selectedIncidentId) {
      return incidentList.find((inc: any) => inc.incident_id === selectedIncidentId) || incidentList[0];
    }
    return incidentList[0];
  }, [incidentList, selectedIncidentId]);

  // Mutation for POST /api/v1/agents/trace
  const simulateMutation = useMutation({
    mutationFn: api.simulateFlow,
    onSuccess: (data: SimulateFlowResponse) => {
      setActiveCorrelationId(data.correlation_id);
      setEventTrace(data.events);

      setNodeEvents((prev) => {
        const nextMap = { ...prev };
        data.events.forEach((evt) => {
          if (!nextMap[evt.source_node]) nextMap[evt.source_node] = [];
          if (!nextMap[evt.target_node]) nextMap[evt.target_node] = [];
          nextMap[evt.source_node].unshift(evt);
          nextMap[evt.target_node].unshift(evt);
        });
        return nextMap;
      });
    },
  });

  // Mutation for Human Approval
  const approveMutation = useMutation({
    mutationFn: (id: string) => api.approveIncident(id, 'Approved via 3D incident control panel'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents_list'] });
    },
  });

  // WebSocket for Verified Flow Replay
  const [socketRef, setSocketRef] = useState<WebSocket | null>(null);

  useEffect(() => {
    let ws: WebSocket | null = null;
    try {
      const wsUrl = api.getReplayStreamWsUrl(selectedDomain, streamSpeed, streamSeed);
      ws = new WebSocket(wsUrl);
      setSocketRef(ws);

      ws.onopen = () => {
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);

          // Stage start: mark node RUNNING
          if (msg.type === 'flow_event' && msg.event_type === 'stage_start' && msg.stage) {
            setNodeStatusMap((prev) => ({
              ...prev,
              [msg.stage]: 'running',
            }));
          }

          // Stage end: mark node SUCCESS, SKIPPED, or FAILED
          if (msg.type === 'flow_event' && msg.event_type === 'stage_end' && msg.stage) {
            const rawStatus = (msg.status || '').toUpperCase();
            const nodeState: NodeState =
              rawStatus === 'SUCCESS' ? 'success' : rawStatus === 'SKIPPED' ? 'skipped' : 'failed';

            setNodeStatusMap((prev) => ({
              ...prev,
              [msg.stage]: nodeState,
            }));

            setNodeMetrics((prev) => ({
              ...prev,
              [msg.stage]: {
                duration_ms: msg.duration_ms,
                input: msg.input_summary,
                output: msg.output_summary,
                error: msg.error,
              },
            }));

            if (msg.event) {
              const evt = msg.event as FlowEventItem;
              setEventTrace((prev) => [evt, ...prev.slice(0, 49)]);
              setNodeEvents((prev) => {
                const nextMap = { ...prev };
                if (!nextMap[evt.source_node]) nextMap[evt.source_node] = [];
                if (!nextMap[evt.target_node]) nextMap[evt.target_node] = [];
                nextMap[evt.source_node].unshift(evt);
                nextMap[evt.target_node].unshift(evt);
                return nextMap;
              });
            }
          }

          // Flow completed
          if (msg.type === 'flow_completed') {
            setActiveCorrelationId(msg.correlation_id);
          }
        } catch (e) {
          console.warn('WS message parse error:', e);
        }
      };

      ws.onclose = () => setWsConnected(false);
      ws.onerror = () => setWsConnected(false);
    } catch (e) {
      console.warn('WebSocket connection error:', e);
    }

    return () => {
      if (ws) ws.close();
    };
  }, [selectedDomain, streamSpeed, streamSeed]);

  // WebSocket Controls
  const sendWsAction = useCallback(
    (actionData: Record<string, any>) => {
      if (socketRef && socketRef.readyState === WebSocket.OPEN) {
        socketRef.send(JSON.stringify(actionData));
      }
    },
    [socketRef]
  );

  const togglePause = useCallback(() => {
    if (isPaused) {
      sendWsAction({ action: 'resume' });
      setIsPaused(false);
    } else {
      sendWsAction({ action: 'pause' });
      setIsPaused(true);
    }
  }, [isPaused, sendWsAction]);

  const changeSpeed = useCallback(
    (speed: number) => {
      setStreamSpeed(speed);
      sendWsAction({ action: 'speed', value: speed });
    },
    [sendWsAction]
  );

  const changeDomain = useCallback(
    (dom: 'nfton' | 'ciciot') => {
      setSelectedDomain(dom);
      sendWsAction({ action: 'domain', value: dom });
    },
    [sendWsAction]
  );

  const nodes = topologyData?.nodes || [];
  const edges = topologyData?.edges || [];
  const nodeEventList = selectedNode ? nodeEvents[selectedNode.id] || [] : [];
  const selectedNodeMetric = selectedNode
    ? nodeMetrics[selectedNode.id.toUpperCase()] || nodeMetrics[selectedNode.id.toLowerCase()]
    : null;

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100 font-mono flex items-center gap-2">
            <Activity className="w-6 h-6 text-cyan-400" />
            <span>Agent Architecture & 3D System Topology</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Dynamic 3D visualization: Live Topology, Domain Shift PCA & CORAL, TreeSHAP Attributions, and Decision Timeline.
          </p>
        </div>

        <ProvenanceBadge
          sourceFile="src/argus/api/routers/stream.py"
          protocolStatus="final"
        />
      </div>

      {/* Top Controls Bar */}
      <Card className="flex flex-wrap items-center justify-between gap-4">
        {/* View Mode Navigation Tabs */}
        <div className="flex flex-wrap items-center gap-2" role="tablist" aria-label="Visualization Scenes">
          <div className="flex items-center bg-slate-950/90 border border-slate-800 rounded-lg p-1">
            <button
              role="tab"
              aria-selected={viewMode === '3D_TOPOLOGY'}
              onClick={() => setViewMode('3D_TOPOLOGY')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all ${
                viewMode === '3D_TOPOLOGY'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(6,182,212,0.25)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
              }`}
            >
              <Network className="w-3.5 h-3.5" />
              <span>Live Topology</span>
            </button>
            <button
              role="tab"
              aria-selected={viewMode === '3D_DOMAIN_SHIFT'}
              onClick={() => setViewMode('3D_DOMAIN_SHIFT')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all ${
                viewMode === '3D_DOMAIN_SHIFT'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(6,182,212,0.25)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
              }`}
            >
              <GitBranch className="w-3.5 h-3.5" />
              <span>Domain Shift (CORAL)</span>
            </button>
            <button
              role="tab"
              aria-selected={viewMode === '3D_SHAP'}
              onClick={() => setViewMode('3D_SHAP')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all ${
                viewMode === '3D_SHAP'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(6,182,212,0.25)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>3D SHAP Scene</span>
            </button>
            <button
              role="tab"
              aria-selected={viewMode === '3D_DECISION_TIMELINE'}
              onClick={() => setViewMode('3D_DECISION_TIMELINE')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all ${
                viewMode === '3D_DECISION_TIMELINE'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(6,182,212,0.25)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Decision Timeline</span>
            </button>
            <button
              role="tab"
              aria-selected={viewMode === '2D'}
              onClick={() => setViewMode('2D')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all ${
                viewMode === '2D'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(6,182,212,0.25)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>2D SVG Fallback</span>
            </button>
          </div>

          <StatusPill
            status={wsConnected ? 'connected' : 'connecting'}
            label={wsConnected ? 'Verified Flow Replay' : 'WS Connecting'}
          />
        </div>

        {/* Replay Stream & Performance Toggles */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Pause / Resume */}
          <button
            onClick={togglePause}
            aria-label={isPaused ? 'Resume Stream Replay' : 'Pause Stream Replay'}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-cyan-400 hover:bg-slate-800"
          >
            {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
            <span>{isPaused ? 'Resume' : 'Pause'}</span>
          </button>

          {/* Speed Select */}
          <select
            value={streamSpeed}
            onChange={(e) => changeSpeed(parseFloat(e.target.value))}
            aria-label="Replay Speed"
            className="bg-slate-900 border border-slate-800 text-slate-200 text-xs font-mono rounded-lg px-2 py-1.5 focus:outline-none"
          >
            <option value={1}>Speed: 1x</option>
            <option value={5}>Speed: 5x</option>
            <option value={10}>Speed: 10x</option>
            <option value={25}>Speed: 25x</option>
          </select>

          {/* Domain Select */}
          <select
            value={selectedDomain}
            onChange={(e) => changeDomain(e.target.value as 'nfton' | 'ciciot')}
            aria-label="Domain Selector"
            className="bg-slate-900 border border-slate-800 text-slate-200 text-xs font-mono rounded-lg px-2 py-1.5 focus:outline-none"
          >
            <option value="nfton">Domain: NF-ToN</option>
            <option value="ciciot">Domain: CICIoT</option>
          </select>

          {/* Quality Toggle (Target 60 FPS) */}
          <button
            onClick={() => setQuality(quality === 'high' ? 'low' : 'high')}
            aria-label={`Toggle Quality. Currently ${quality === 'high' ? '60 FPS High' : 'Low'}`}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 hover:bg-slate-800"
          >
            <Gauge className="w-3.5 h-3.5 text-amber-400" />
            <span>{quality === 'high' ? 'Quality: 60 FPS' : 'Quality: Eco'}</span>
          </button>

          {/* Reduced Motion Toggle */}
          <button
            onClick={() => setReducedMotion(!reducedMotion)}
            aria-label="Toggle Reduced Motion"
            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg border text-xs font-mono ${
              reducedMotion
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Motion: {reducedMotion ? 'Off' : 'On'}</span>
          </button>

          {/* Trigger Flow Simulation */}
          <button
            onClick={() => simulateMutation.mutate()}
            disabled={simulateMutation.isPending}
            aria-label="Trigger Flow Simulation"
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs font-mono disabled:opacity-50 transition-colors"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>{simulateMutation.isPending ? 'Simulating...' : 'Trigger Flow'}</span>
          </button>

          {/* Reset View */}
          <button
            onClick={() => {
              setSelectedNode(null);
              setActiveCorrelationId(null);
              setEventTrace([]);
              refetchTopology();
            }}
            title="Reset View"
            aria-label="Reset View"
            className="p-2 rounded-lg bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </Card>

      {/* Main Viewport & Detail Panels Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Canvas Viewport (2 Cols) */}
        <Card className="lg:col-span-2 relative h-[580px] p-0 overflow-hidden border border-slate-800 flex flex-col justify-between bg-slate-950">
          {loadingTopology ? (
            <Skeleton className="w-full h-full" />
          ) : (
            <>
              <div className={`w-full h-full ${viewMode === '2D' ? 'hidden' : 'block'}`}>
                <Suspense fallback={<Skeleton className="w-full h-full" />}>
                  <TopologyCanvas3D
                    nodes={nodes}
                    edges={edges}
                    selectedNode={selectedNode}
                    onSelectNode={setSelectedNode}
                    activeEvents={eventTrace}
                    sceneMode={
                      viewMode === '3D_DOMAIN_SHIFT'
                        ? 'DOMAIN_SHIFT'
                        : viewMode === '3D_SHAP'
                        ? 'SHAP'
                        : viewMode === '3D_DECISION_TIMELINE'
                        ? 'DECISION_TIMELINE'
                        : 'TOPOLOGY'
                    }
                    quality={quality}
                    reducedMotion={reducedMotion}
                    shiftData={shiftPCAData}
                    shiftLoading={loadingShiftPCA}
                    selectedIncident={selectedIncident}
                    nodeStatusMap={nodeStatusMap}
                    onApproveIncident={(id) => approveMutation.mutate(id)}
                  />
                </Suspense>
              </div>
              {viewMode === '2D' && (
                <TopologyGraph2D
                  nodes={nodes}
                  edges={edges}
                  selectedNode={selectedNode}
                  onSelectNode={setSelectedNode}
                  activeEvents={eventTrace}
                  layoutMode="architecture"
                />
              )}
            </>
          )}

          {/* Canvas Bottom Overlay Banner */}
          <div className="absolute bottom-3 left-3 right-3 pointer-events-none flex justify-between items-center px-3.5 py-2 rounded-lg bg-slate-950/85 backdrop-blur-md border border-slate-800 text-[11px] font-mono text-slate-400">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              Mode: <strong className="text-cyan-300">{viewMode}</strong>
            </span>
            <span className="text-slate-500 hidden sm:inline">
              Drag to rotate • Scroll to zoom • Click node to inspect I/O & duration
            </span>
            <span className="text-slate-300">
              Quality: <strong className="text-amber-400 uppercase">{quality}</strong> | Motion:{' '}
              <strong className="text-cyan-300">{reducedMotion ? 'REDUCED' : 'ACTIVE'}</strong>
            </span>
          </div>
        </Card>

        {/* Side Panels (1 Col): Detail Panel or Active Trace List */}
        <div className="space-y-6 lg:col-span-1">
          {/* Node Detail & I/O Summary Panel */}
          <Card className="space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h2 className="text-sm font-bold font-mono text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <span>Node Summary & Telemetry</span>
              </h2>
              {selectedNode && (
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-xs text-slate-400 hover:text-slate-200"
                >
                  Clear
                </button>
              )}
            </div>

            {selectedNode ? (
              <div className="space-y-3 text-xs font-mono">
                <div>
                  <div className="text-[10px] text-slate-400 uppercase">Node ID & Type</div>
                  <div className="text-slate-100 font-bold text-sm flex items-center gap-2">
                    <span>{selectedNode.name}</span>
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                      {selectedNode.type}
                    </span>
                  </div>
                </div>

                <div>
                  <div className="text-[10px] text-slate-400 uppercase">Responsibility</div>
                  <div className="text-slate-300 font-sans text-xs mt-0.5">
                    {selectedNode.responsibility}
                  </div>
                </div>

                {/* Live execution duration and status */}
                <div className="grid grid-cols-2 gap-2 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                  <div>
                    <div className="text-[10px] text-slate-400">Live Status</div>
                    <div className="text-cyan-400 font-bold uppercase">
                      {nodeStatusMap[selectedNode.id.toUpperCase()] || 'IDLE'}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-400">Duration</div>
                    <div className="text-emerald-400 font-bold">
                      {selectedNodeMetric?.duration_ms != null
                        ? `${selectedNodeMetric.duration_ms.toFixed(2)} ms`
                        : '0.00 ms'}
                    </div>
                  </div>
                </div>

                {/* Input Summary */}
                {selectedNodeMetric?.input && (
                  <div>
                    <div className="text-[10px] text-slate-400 uppercase">Input Summary</div>
                    <div className="text-slate-200 bg-slate-900 p-2 rounded border border-slate-800 text-[11px]">
                      {selectedNodeMetric.input}
                    </div>
                  </div>
                )}

                {/* Output Summary */}
                {selectedNodeMetric?.output && (
                  <div>
                    <div className="text-[10px] text-slate-400 uppercase">Output Summary</div>
                    <div className="text-emerald-300 bg-slate-900 p-2 rounded border border-slate-800 text-[11px]">
                      {selectedNodeMetric.output}
                    </div>
                  </div>
                )}

                {/* Error Trace if Failed */}
                {selectedNodeMetric?.error && (
                  <div>
                    <div className="text-[10px] text-rose-400 uppercase">Failure Error</div>
                    <div className="text-rose-300 bg-rose-950/40 p-2 rounded border border-rose-800 text-[11px]">
                      {selectedNodeMetric.error}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-4 text-center text-slate-500 font-mono text-xs">
                Click any agent node in the 3D scene to inspect live input/output summary, execution duration, and operational state.
              </div>
            )}
          </Card>

          {/* Active Event Trace Stream List */}
          <Card className="space-y-3">
            <h2 className="text-sm font-bold font-mono text-slate-900 dark:text-slate-100 flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                <span>Verified Flow Replay Traces</span>
              </span>
              <span className="text-[10px] font-normal text-slate-400">
                {eventTrace.length} events
              </span>
            </h2>

            <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
              {eventTrace.length > 0 ? (
                eventTrace.slice(0, 10).map((evt, idx) => (
                  <div
                    key={`${evt.event_id}-${idx}`}
                    data-testid="flow-event-item"
                    className="p-2 rounded bg-slate-900/60 border border-slate-800 text-[11px] font-mono"
                  >
                    <div className="flex items-center justify-between text-slate-400 text-[9px] mb-1">
                      <span>{evt.source_node} → {evt.target_node}</span>
                      <span className="text-cyan-400">{evt.event_type}</span>
                    </div>
                    <div className="text-slate-200 truncate">{evt.summary}</div>
                  </div>
                ))
              ) : (
                <div className="p-4 text-center text-slate-500 font-mono text-xs">
                  Streaming verified domain telemetry from dataset/{selectedDomain}.parquet...
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
