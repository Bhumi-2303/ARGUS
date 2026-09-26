import React from 'react';
import { Incident } from '../services/api';
import { Activity, ShieldAlert, BookOpen, BrainCircuit, Gavel, PlaySquare } from 'lucide-react';

interface Props {
  incident: Incident;
}

const AgentTrace: React.FC<Props> = ({ incident }) => {
  const stages = [
    { name: 'Detector', icon: Activity, status: incident.detector_summary ? 'completed' : 'pending' },
    { name: 'Risk', icon: ShieldAlert, status: incident.risk_score ? 'completed' : 'pending' },
    { name: 'Knowledge', icon: BookOpen, status: incident.knowledge_summary ? 'completed' : 'pending' },
    { name: 'Explainability', icon: BrainCircuit, status: incident.model_provenance ? 'completed' : 'pending' },
    { name: 'Decision', icon: Gavel, status: incident.decision ? 'completed' : 'pending' },
    { name: 'Response', icon: PlaySquare, status: incident.response ? 'completed' : (incident.approval_status === 'PENDING' ? 'running' : 'pending') }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
      <h3 className="text-sm font-semibold text-slate-300 mb-6 flex items-center gap-2">
        <BrainCircuit className="w-4 h-4 text-slate-400" />
        Agent Execution Pipeline
      </h3>
      
      <div className="relative">
        <div className="absolute top-1/2 left-4 right-4 h-0.5 bg-slate-800 -translate-y-1/2 z-0" />
        <div className="relative z-10 flex justify-between">
          {stages.map((stage, idx) => {
            const Icon = stage.icon;
            let bgColor = 'bg-slate-950 border-slate-700 text-slate-500';
            if (stage.status === 'completed') bgColor = 'bg-slate-800 border-blue-500/50 text-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.2)]';
            if (stage.status === 'running') bgColor = 'bg-slate-800 border-amber-500/50 text-amber-400 shadow-[0_0_10px_rgba(245,158,11,0.2)] animate-pulse';

            return (
              <div key={idx} className="flex flex-col items-center gap-2 group cursor-pointer">
                <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center transition-all ${bgColor}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-mono font-medium text-slate-400 group-hover:text-slate-200 transition-colors uppercase">
                  {stage.name}
                </span>
              </div>
            );
          })}
        </div>
      </div>
      <div className="mt-6 p-4 bg-slate-950 rounded border border-slate-800/50 text-xs font-mono text-slate-400">
        <p className="text-slate-500 mb-2">// Select a stage in the pipeline above to view execution details</p>
        <p>Execution trace visualization provides inspectability for operational review. ARGUS agents follow defined policies and do not act autonomously beyond approved bounds.</p>
      </div>
    </div>
  );
};

export default AgentTrace;
