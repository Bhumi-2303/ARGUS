import React, { useMemo } from 'react';
import { useParams, Link, Navigate } from 'react-router-dom';
import { agents } from '../services/api';
import { Activity, ArrowRight, ArrowLeft, Terminal, CheckCircle2, ShieldAlert, Eye, Brain, FileText, Network } from 'lucide-react';
import { AgentId } from '../types';

const iconMap: Record<string, any> = {
  'ag-detect': Eye,
  'ag-assess': Activity,
  'ag-explain': Brain,
  'ag-respond': ShieldAlert,
  'ag-report': FileText,
};

export default function AgentDetails() {
  const { agentId } = useParams<{ agentId: string }>();
  
  const agent = useMemo(() => agents.find(a => a.id === agentId), [agentId]);
  
  if (!agent) {
    return <Navigate to="/pipeline" replace />;
  }

  const Icon = iconMap[agent.id] || Activity;

  // Mini-pipeline visualization
  const MiniPipeline = () => (
    <div className="flex items-center justify-between bg-slate-900/50 border border-slate-800 rounded-xl p-4 mb-8 overflow-x-auto">
      {agents.map((a, i) => {
        const isCurrent = a.id === agent.id;
        const AIcon = iconMap[a.id] || Activity;
        return (
          <React.Fragment key={a.id}>
            <Link to={`/pipeline/${a.id}`} className="flex flex-col items-center group shrink-0 outline-none">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all shadow-md ${
                isCurrent 
                  ? 'bg-blue-600 border-2 border-blue-400 text-white ring-4 ring-blue-900/50' 
                  : 'bg-slate-800 border border-slate-700 text-slate-400 group-hover:bg-slate-700 group-hover:text-slate-200'
              }`}>
                <AIcon className="w-5 h-5" />
              </div>
              <span className={`text-[10px] mt-2 font-bold uppercase tracking-wider ${isCurrent ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-300'}`}>
                {a.name.replace(' Agent', '')}
              </span>
            </Link>
            {i < agents.length - 1 && (
              <div className="flex-1 h-0.5 mx-2 bg-slate-800 relative min-w-[20px]">
                <div className={`absolute top-0 left-0 h-full ${agents.findIndex(x => x.id === agent.id) > i ? 'bg-blue-500' : 'bg-transparent'}`} style={{ width: '100%' }}></div>
              </div>
            )}
          </React.Fragment>
        )
      })}
    </div>
  );

  const getAgentName = (id: string) => {
    if (id === 'Network Traffic' || id === 'Audit Trail') return id;
    const a = agents.find(x => x.id === id);
    return a ? a.name : id;
  };

  return (
    <div className="flex flex-col gap-6 h-full pb-10 max-w-5xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div className="flex items-center gap-5">
          <div className="w-16 h-16 bg-slate-800 border border-slate-700 rounded-2xl flex items-center justify-center shadow-inner">
            <Icon className="w-8 h-8 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold tracking-tight text-slate-100">{agent.name}</h1>
              {agent.status === 'Active' && (
                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  Active
                </span>
              )}
            </div>
            <p className="text-slate-400 text-sm">{agent.roleSummary}</p>
          </div>
        </div>
        
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 min-w-[250px]">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Current Task</span>
          <div className="flex items-center gap-2 text-sm text-slate-200 font-medium">
            <Activity className="w-4 h-4 text-blue-500" />
            {agent.currentTask}
          </div>
        </div>
      </div>

      <MiniPipeline />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Details */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="glass-panel p-6">
            <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-4 border-b border-slate-800 pb-2">Processing Core</h2>
            <p className="text-slate-300 leading-relaxed text-sm">{agent.processing}</p>
          </div>

          <div className="glass-panel p-6">
            <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-4 border-b border-slate-800 pb-2">Responsibilities</h2>
            <ul className="space-y-3">
              {agent.responsibilities.map((resp, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                  <CheckCircle2 className="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
                  <span>{resp}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* I/O Tags */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-panel p-6 bg-slate-900/80 border-dashed">
              <h2 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-3">Expected Input</h2>
              <div className="flex flex-wrap gap-2">
                {agent.input.map((inp, i) => (
                  <span key={i} className="px-2.5 py-1 bg-slate-800 border border-slate-700 rounded-md text-xs text-slate-300">
                    {inp}
                  </span>
                ))}
              </div>
            </div>
            <div className="glass-panel p-6 bg-slate-900/80 border-dashed">
              <h2 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-3">Generated Output</h2>
              <div className="flex flex-wrap gap-2">
                {agent.output.map((out, i) => (
                  <span key={i} className="px-2.5 py-1 bg-blue-900/20 border border-blue-800/50 rounded-md text-xs text-blue-300 font-medium">
                    {out}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="flex flex-col gap-6">
          {/* Communication Flow */}
          <div className="glass-panel p-6 bg-blue-950/10 border-blue-900/20">
            <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-5 border-b border-slate-800 pb-2">Communication Flow</h2>
            
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Receives From</span>
                {agent.receivesFrom === 'Network Traffic' ? (
                  <div className="p-3 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-300 flex items-center gap-2">
                    <Network className="w-4 h-4 text-slate-500" />
                    Network Traffic
                  </div>
                ) : (
                  <Link to={`/pipeline/${agent.receivesFrom}`} className="p-3 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-2 group">
                    <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                    {getAgentName(agent.receivesFrom)}
                  </Link>
                )}
              </div>

              <div className="flex justify-center py-2">
                <div className="w-px h-6 bg-slate-700 relative">
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-blue-500 ring-4 ring-slate-950"></div>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Sends To</span>
                {agent.sendsTo === 'Audit Trail' ? (
                  <div className="p-3 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-300 flex items-center gap-2">
                    <FileText className="w-4 h-4 text-slate-500" />
                    Audit Trail
                  </div>
                ) : (
                  <Link to={`/pipeline/${agent.sendsTo}`} className="p-3 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm text-emerald-400 hover:text-emerald-300 transition-colors flex items-center gap-2 group justify-between">
                    {getAgentName(agent.sendsTo)}
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </Link>
                )}
              </div>
            </div>
          </div>

          {/* Execution Trace */}
          <div className="glass-panel p-0 overflow-hidden flex flex-col flex-1 min-h-[250px]">
            <div className="p-4 border-b border-slate-800 bg-slate-900/50 flex items-center gap-2">
              <Terminal className="w-4 h-4 text-slate-400" />
              <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Live Execution Trace</h2>
            </div>
            <div className="p-4 bg-black/40 flex-1 font-mono text-xs overflow-y-auto">
              <div className="flex flex-col gap-3">
                {agent.executionTrace.map((trace, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <span className="text-slate-500 shrink-0">[{trace.timestamp}]</span>
                    <span className="text-emerald-400/90">{trace.step}</span>
                  </div>
                ))}
                <div className="flex items-start gap-3 animate-pulse">
                  <span className="text-slate-500 shrink-0">[{new Date().toLocaleTimeString('en-US', { hour12: false })}]</span>
                  <span className="text-slate-400">Waiting for next event...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
