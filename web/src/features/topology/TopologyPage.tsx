import React, { useState, useEffect, Suspense } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Activity,
  Play,
  RotateCcw,
  Eye,
  Layers,
  Info,
  CheckCircle2,
  AlertTriangle,
  Server,
  Zap,
  Cpu,
} from 'lucide-react';
import { api, TopologyNode, TopologyEdge, FlowEventItem, SimulateFlowResponse } from '../../api/client';
import { ProvenanceBadge } from '../../components/ProvenanceBadge';
import { Card } from '../../components/Card';
import { Skeleton } from '../../components/Skeleton';
import { StatusPill } from '../../components/StatusPill';
import { TopologyCanvas3D } from './TopologyCanvas3D';
import { TopologyGraph2D } from './TopologyGraph2D';

export default function TopologyPage() {
  const [viewMode, setViewMode] = useState<'3D' | '2D'>('3D');
  const [selectedNode, setSelectedNode] = useState<TopologyNode | null>(null);
  const [activeCorrelationId, setActiveCorrelationId] = useState<string | null>(null);
  const [eventTrace, setEventTrace] = useState<FlowEventItem[]>([]);
  const [nodeEvents, setNodeEvents] = useState<Record<string, FlowEventItem[]>>({});
  const [wsConnected, setWsConnected] = useState<boolean>(false);

  // Fetch Topology graph definition
  const { data: topologyData, isLoading: loadingTopology, refetch: refetchTopology } = useQuery({
    queryKey: ['agent_topology'],
    queryFn: api.getTopology,
  });

  // Mutation for POST /api/v1/agents/trace
  const simulateMutation = useMutation({
    mutationFn: api.simulateFlow,
    onSuccess: (data: SimulateFlowResponse) => {
      setActiveCorrelationId(data.correlation_id);
      setEventTrace(data.events);

      // Group events by node ID
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

  // WebSocket for real-time status and flow event broadcasting
  useEffect(() => {
    let socket: WebSocket | null = null;
    try {
      const wsUrl = api.getAgentStreamWsUrl();
      socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        setWsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'flow_event' && msg.event) {
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
        } catch (e) {
          console.warn('WS message parse error:', e);
        }
      };

      socket.onclose = () => setWsConnected(false);
      socket.onerror = () => setWsConnected(false);
    } catch (e) {
      console.warn('WebSocket connection error:', e);
    }

    return () => {
      if (socket) socket.close();
    };
  }, []);

  const nodes = topologyData?.nodes || [];
  const edges = topologyData?.edges || [];

  const nodeEventList = selectedNode ? nodeEvents[selectedNode.id] || [] : [];


  const AGENTS = [
    { id: 'data_intelligence', name: 'Data Intelligence' },
    { id: 'threat_analysis', name: 'Threat Analysis' },
    { id: 'explainability', name: 'Explainability' },
    { id: 'knowledge_context', name: 'Knowledge Context' },
    { id: 'risk_prediction', name: 'Risk Prediction' },
    { id: 'decision_support', name: 'Decision Support' }
  ];

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100 font-mono flex items-center gap-2">
            <Activity className="w-6 h-6 text-cyan-400" />
            <span>Agent Architecture & System Topology View</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Dynamic 3D/2D visualization of agent nodes, responsibility routing, live WebSocket status, and flow execution tracing.
          </p>
        </div>

        <ProvenanceBadge
          sourceFile="src/argus/api/routers/agents.py"
          protocolStatus="final"
        />
      </div>

      {/* Top Controls Bar */}
      <Card className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setViewMode(viewMode === '3D' ? '2D' : '3D')}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs font-mono border border-slate-700 transition-colors"
          >
            <Eye className="w-4 h-4 text-cyan-400" />
            <span>Switch to {viewMode === '3D' ? '2D Fallback View' : '3D WebGL View'}</span>
          </button>

          <StatusPill
            status={wsConnected ? 'connected' : 'connecting'}
            label={wsConnected ? 'WebSocket Live' : 'WS Reconnecting'}
          />
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => simulateMutation.mutate()}
            disabled={simulateMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-700 text-white font-medium text-xs font-mono uppercase tracking-wider transition-colors disabled:opacity-50"
          >
            <Play className="w-4 h-4" />
            <span>{simulateMutation.isPending ? 'Traced Event Flow...' : 'Trigger Real Flow'}</span>
          </button>

          <button
            onClick={() => {
              setSelectedNode(null);
              setActiveCorrelationId(null);
              setEventTrace([]);
              refetchTopology();
            }}
            title="Reset View & Clear Event Traces"
            className="p-2 rounded-lg bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </Card>

      {/* Main Viewport & Detail Panels Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Canvas Viewport (2 Cols) */}
        <Card className="lg:col-span-2 relative h-[520px] p-0 overflow-hidden border border-slate-800 flex flex-col justify-between">
          {loadingTopology ? (
            <Skeleton className="w-full h-full" />
          ) : viewMode === '3D' ? (
            <Suspense fallback={<Skeleton className="w-full h-full" />}>
              <TopologyCanvas3D
                nodes={nodes}
                edges={edges}
                selectedNode={selectedNode}
                onSelectNode={setSelectedNode}
                activeEvents={eventTrace}
              />
            </Suspense>
          ) : (
            <TopologyGraph2D
              nodes={nodes}
              edges={edges}
              selectedNode={selectedNode}
              onSelectNode={setSelectedNode}
              activeEvents={eventTrace}
            />
          )}

          {/* Canvas Bottom Overlay Banner */}
          <div className="absolute bottom-3 left-3 right-3 pointer-events-none flex justify-between items-center px-3 py-2 rounded-lg bg-slate-950/80  border border-slate-800 text-xs font-mono text-slate-400">
            <span>Nodes: <strong className="text-cyan-300">{nodes.length}</strong> | Connections: <strong className="text-cyan-300">{edges.length}</strong></span>
            <span>View Mode: <strong className="text-slate-200">{viewMode}</strong></span>
          </div>
        </Card>

        {/* Side Panels (1 Col): Detail Panel or Active Trace List */}
        <div className="space-y-6 lg:col-span-1">
          {/* Node Detail Panel */}
          <Card className="space-y-3">
            <h2 className="text-sm font-bold font-mono text-slate-900 dark:text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>Node Responsibility Detail Panel</span>
            </h2>

            {selectedNode ? (
              <div className="space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-base font-bold text-slate-900 dark:text-slate-100">{selectedNode.name}</span>
                  <StatusPill status={selectedNode.status} />
                </div>

                <div className="p-2.5 rounded bg-slate-950/80 border border-slate-800 space-y-1">
                  <span className="text-slate-500 text-[10px] block">Node ID</span>
                  <span className="text-cyan-300 font-bold">{selectedNode.id}</span>
                </div>

                <div className="p-2.5 rounded bg-slate-950/80 border border-slate-800 space-y-1">
                  <span className="text-slate-500 text-[10px] block">API Stated Responsibility</span>
                  <p className="text-slate-300 font-sans text-xs leading-relaxed">
                    {selectedNode.responsibility}
                  </p>
                </div>

                <div className="flex items-center justify-between p-2.5 rounded bg-slate-950/80 border border-slate-800">
                  <span className="text-slate-400 text-[10px]">Implementation Flag</span>
                  {selectedNode.implementation_type === 'stub' ? (
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold text-[10px]">
                      STUB / IN-PROGRESS
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold text-[10px]">
                      FULLY IMPLEMENTED
                    </span>
                  )}
                </div>

                {/* Node Events Sub-list */}
                <div className="space-y-1 pt-1">
                  <span className="text-slate-400 text-[10px] block font-bold">Node Event History ({nodeEventList.length})</span>
                  {nodeEventList.length === 0 ? (
                    <div className="text-slate-500 text-[11px] font-sans">No events logged for this node.</div>
                  ) : (
                    <div className="max-h-36 overflow-y-auto space-y-1.5 divide-y divide-slate-800/40">
                      {nodeEventList.slice(0, 5).map((evt) => (
                        <div key={evt.event_id} className="pt-1.5 text-[11px]">
                          <div className="flex justify-between text-slate-400">
                            <span className="text-cyan-400">{evt.event_type}</span>
                            <span className="text-[10px]">{evt.timestamp.slice(11, 19)}</span>
                          </div>
                          <p className="text-slate-300 font-sans">{evt.summary}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="p-6 text-center text-slate-500 font-mono text-xs border border-dashed border-slate-800 rounded-lg">
                Click any 3D/2D node in the graph to inspect agent responsibility, implementation status, and event history.
              </div>
            )}
          </Card>

          {/* Active Flow Trace Side Panel */}
          <Card className="space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h2 className="text-sm font-bold font-mono text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Zap className="w-4 h-4 text-emerald-400" />
                <span>Live Event Trace Log</span>
              </h2>
              {activeCorrelationId && (
                <span className="text-[10px] font-mono text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
                  {activeCorrelationId}
                </span>
              )}
            </div>

            {eventTrace.length === 0 ? (
              <div className="p-6 text-center text-slate-500 font-mono text-xs border border-dashed border-slate-800 rounded-lg">
                No active event trace. Click "Trigger Real Flow" above to execute an end-to-end multi-step flow.
              </div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto font-mono text-xs pr-1 divide-y divide-slate-800/40">
                {eventTrace.map((evt) => (
                  <div key={evt.event_id} className="pt-2 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-cyan-400 font-bold">{evt.source_node} → {evt.target_node}</span>
                      <span className="text-slate-500 text-[10px]">{evt.timestamp.slice(11, 19)}</span>
                    </div>
                    <p className="text-slate-300 font-sans text-xs">{evt.summary}</p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>

      {/* Agent Implementation & Live Readiness Status Matrix */}
      <Card className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
          <h2 className="text-sm font-bold font-mono text-slate-100 flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>Agent Execution Results</span>
          </h2>
          <span className="text-xs font-mono text-slate-400">Strict honest reporting — zero fake completion</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 font-mono text-xs">
          {AGENTS.map((agent, index) => {
            // Find the trace event for this agent
            // Note: eventTrace might have target_node matching the agent id
            const traceEvent = eventTrace.find(e => e.target_node.toLowerCase() === agent.id.toLowerCase());
            
            let status = 'WAITING';
            let duration = null;
            let output = 'Awaiting execution...';
            let error = null;
            let statusColor = 'bg-slate-800 text-slate-400';

            if (traceEvent && traceEvent.payload) {
              status = traceEvent.payload.status;
              duration = traceEvent.payload.duration_ms;
              output = traceEvent.payload.output || traceEvent.summary || 'No output summary provided.';
              error = traceEvent.payload.error;

              if (status === 'SUCCESS') statusColor = 'bg-emerald-500/20 text-emerald-300';
              else if (status === 'FAILED') statusColor = 'bg-red-500/20 text-red-300';
              else if (status === 'SKIPPED') statusColor = 'bg-amber-500/20 text-amber-300';
              else statusColor = 'bg-blue-500/20 text-blue-300';
            }

            return (
              <div key={agent.id} className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-slate-200">
                      {index + 1}. {agent.name}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${statusColor}`}>
                      {status}
                    </span>
                  </div>
                  {duration !== null && duration !== undefined && typeof duration === 'number' && (
                    <div className="text-[10px] text-slate-500 mb-2">
                      Duration: {duration.toFixed(2)}ms
                    </div>
                  )}
                  {error ? (
                    <div className="text-[11px] text-red-400 font-sans leading-relaxed p-2 bg-red-950/30 rounded border border-red-900/50">
                      <strong>Error:</strong> {error}
                    </div>
                  ) : (
                    <p className="text-[11px] text-slate-400 font-sans leading-relaxed">
                      {output}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
