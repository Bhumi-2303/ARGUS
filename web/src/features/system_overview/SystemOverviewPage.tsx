import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, ModelInfo } from '../../api/client';
import { Card } from '../../components/Card';
import { MetricTile } from '../../components/MetricTile';
import { DataTable, Column } from '../../components/DataTable';
import { StatusPill } from '../../components/StatusPill';
import { ProvenanceBadge } from '../../components/ProvenanceBadge';
import { Skeleton } from '../../components/Skeleton';
import { EmptyState } from '../../components/EmptyState';
import { useLiveStream } from '../../hooks/useLiveStream';
import {
  Activity,
  Cpu,
  Layers,
  Play,
  Pause,
  RotateCcw,
  Zap,
  Server,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

export default function SystemOverviewPage() {
  // Query 1: Health
  const healthQuery = useQuery({
    queryKey: ['health'],
    queryFn: api.getHealth,
    refetchInterval: 10000,
  });

  // Query 2: Models
  const modelsQuery = useQuery({
    queryKey: ['models'],
    queryFn: api.getModels,
    refetchInterval: 30000,
  });

  // Live stream hook
  const stream = useLiveStream({ domain: 'ciciot', autoConnect: false });

  const isHealthLoading = healthQuery.isLoading;
  const isModelsLoading = modelsQuery.isLoading;
  const healthError = healthQuery.error;
  const modelsError = modelsQuery.error;

  const modelsData = modelsQuery.data?.models || [];
  const modelsCount = modelsQuery.data?.count || 0;
  const isHealthy = healthQuery.data?.status === 'healthy';

  const columns: Column<ModelInfo>[] = [
    {
      key: 'name',
      header: 'Model Name',
      render: (m) => (
        <div className="font-semibold text-slate-100 flex items-center gap-2">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span>{m.name}</span>
        </div>
      ),
    },
    {
      key: 'protocol_status',
      header: 'Protocol Status',
      render: (m) => <StatusPill status={m.protocol_status} pulse={false} />,
    },
    {
      key: 'source_domain',
      header: 'Source',
      render: (m) => <span className="uppercase text-slate-300 font-mono text-[11px]">{m.source_domain}</span>,
    },
    {
      key: 'target_domain',
      header: 'Target',
      render: (m) => <span className="uppercase text-slate-300 font-mono text-[11px]">{m.target_domain}</span>,
    },
    {
      key: 'threshold',
      header: 'Decision Threshold',
      render: (m) => (
        <span className="font-mono text-cyan-300 font-semibold">{m.threshold.toFixed(2)}</span>
      ),
    },
    {
      key: 'provenance',
      header: 'Adaptation Method',
      render: (m) => (
        <span className="text-slate-400 text-[11px]">{m.provenance?.adaptation_method || 'N/A'}</span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-100">
              ARGUS Platform Verification & Wiring Overview
            </h1>
            <StatusPill
              status={isHealthy ? 'healthy' : healthError ? 'error' : 'connecting'}
              label={isHealthy ? 'Backend API Live' : healthError ? 'API Unreachable' : 'Connecting'}
            />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time verification of FastAPI REST backend (<code className="text-cyan-300 font-mono">/health</code>,{' '}
            <code className="text-cyan-300 font-mono">/api/v1/models</code>), model registry, and live stream telemetry wiring.
          </p>
        </div>

        <ProvenanceBadge
          sourceFile="artifacts/models/registry.yaml"
          protocolStatus="final"
          dataset="CICIoT2023 / NF-ToN-IoT / IEC104"
        />
      </div>

      {/* Metric Tiles Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isHealthLoading || isModelsLoading ? (
          <>
            <Skeleton variant="card" />
            <Skeleton variant="card" />
            <Skeleton variant="card" />
            <Skeleton variant="card" />
          </>
        ) : (
          <>
            <MetricTile
              title="API Server Status"
              value={healthQuery.data?.status?.toUpperCase() || 'OFFLINE'}
              subtitle="FastAPI backend runtime on localhost:8000"
              icon={<Server className="w-5 h-5 text-emerald-400" />}
              sourceFile="src/argus/api/main.py"
              protocolStatus="final"
            />

            <MetricTile
              title="Registered Models"
              value={modelsCount}
              subtitle="In-memory loaded ML boosters & neural models"
              icon={<Layers className="w-5 h-5 text-cyan-400" />}
              sourceFile="src/argus/registry/model_registry.py"
              protocolStatus="final"
            />

            <MetricTile
              title="Clean CORAL Alignment"
              value={`${(modelsData.find(m => m.name === 'model_d2_coral')?.threshold ?? 0.99).toFixed(2)} Threshold`}
              subtitle="Optimal MCC calibrated operating point"
              icon={<ShieldCheck className="w-5 h-5 text-purple-400" />}
              sourceFile="results/verified/five_model_complete_comparison.csv"
              protocolStatus="final"
            />


            <MetricTile
              title="Live Stream Status"
              value={stream.status.toUpperCase()}
              subtitle={`${stream.events.length} events buffered (${stream.speed}x speed)`}
              icon={<Zap className="w-5 h-5 text-amber-400" />}
              sourceFile="src/argus/api/routers/stream.py"
              protocolStatus="demo-scale"
            />
          </>
        )}
      </div>

      {/* Model Registry Section */}
      <Card
        title="Loaded Model Registry Artifacts (/api/v1/models)"
        subtitle="Verifies model artifact deserialization and metadata registry endpoints"
        action={
          <span className="text-xs font-mono text-cyan-400 bg-cyan-500/10 border border-cyan-500/30 px-2.5 py-1 rounded-full">
            {modelsCount} Active Artifacts
          </span>
        }
      >
        {isModelsLoading ? (
          <Skeleton variant="table" />
        ) : modelsError ? (
          <EmptyState
            title="Failed to Load Model Registry"
            description={`Error connecting to FastAPI backend: ${(modelsError as Error).message}`}
            icon={<AlertCircle className="w-6 h-6 text-rose-400" />}
            action={{
              label: 'Retry Fetch',
              onClick: () => modelsQuery.refetch(),
            }}
          />
        ) : modelsData.length === 0 ? (
          <EmptyState
            title="No Models Registered"
            description="The FastAPI backend model registry reported zero loaded models."
          />
        ) : (
          <DataTable columns={columns} data={modelsData} pageSize={10} searchPlaceholder="Filter models..." />
        )}
      </Card>

      {/* Live Stream Harness Wiring Card */}
      <Card
        title="Live Stream Telemetry Harness (useLiveStream Hook)"
        subtitle="Demonstrates real-time telemetry streaming, speed adjustment, pause/resume, and auto-reconnect"
        variant="glass"
      >
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="flex items-center gap-3">
              <StatusPill status={stream.status} />
              <span className="text-xs font-mono text-slate-300">
                Buffered: <strong className="text-slate-100">{stream.events.length}</strong> events | Anomaly Detections:{' '}
                <strong className="text-rose-400">{stream.anomalyCount}</strong>
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400 mr-1 font-mono">Stream Speed:</span>
              {[1, 2, 5, 10].map((s) => (
                <button
                  key={s}
                  onClick={() => stream.setSpeed(s)}
                  className={`px-2.5 py-1 text-xs font-mono font-semibold rounded-md border transition-all ${
                    stream.speed === s
                      ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-sm shadow-cyan-500/20'
                      : 'bg-slate-900 text-slate-400 border-slate-700 hover:bg-slate-800 hover:text-slate-200'
                  }`}
                >
                  {s}x
                </button>
              ))}

              <div className="h-4 w-px bg-slate-800 mx-1" />

              {stream.isPaused ? (
                <button
                  onClick={stream.resume}
                  className="flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30 transition-colors"
                >
                  <Play className="w-3.5 h-3.5" /> Start Stream
                </button>
              ) : (
                <button
                  onClick={stream.pause}
                  className="flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 transition-colors"
                >
                  <Pause className="w-3.5 h-3.5" /> Pause Stream
                </button>
              )}

              <button
                onClick={stream.clear}
                title="Clear Events"
                className="p-1 text-slate-400 hover:text-slate-200 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {stream.events.length === 0 ? (
            <div className="p-6 text-center border border-dashed border-slate-800 rounded-lg text-slate-500 text-xs font-mono">
              Stream paused or waiting for events. Click "Start Stream" above to activate live telemetry stream.
            </div>
          ) : (
            <div className="space-y-2 font-mono text-xs max-h-48 overflow-y-auto pr-1 divide-y divide-slate-800/40">
              {stream.events.slice(0, 5).map((evt, idx) => (
                <div key={idx} className="pt-2 flex items-center justify-between text-slate-300">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-500 text-[10px]">{evt.timestamp || new Date().toISOString()}</span>
                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-cyan-300">{evt.domain}</span>
                    <span className="text-slate-400">pkt_mean_to_max: {evt.features?.pkt_mean_to_max?.toFixed(3)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 text-[10px]">Score: {evt.anomaly_score?.toFixed(4)}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        evt.prediction === 1
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      {evt.prediction === 1 ? 'ATTACK' : 'BENIGN'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
