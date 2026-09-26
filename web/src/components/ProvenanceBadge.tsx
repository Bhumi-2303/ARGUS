import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, Info, FileText, ExternalLink } from 'lucide-react';
import { clsx } from 'clsx';

export type ProtocolStatus =
  | 'final'
  | 'diagnostic-only'
  | 'demo-scale'
  | 'requires verification';

export interface ProvenanceBadgeProps {
  sourceFile?: string;
  protocolStatus?: ProtocolStatus;
  dataset?: string;
  adaptationMethod?: string;
  className?: string;
  compact?: boolean;
}

export const ProvenanceBadge: React.FC<ProvenanceBadgeProps> = ({
  sourceFile = 'results/verified/five_model_complete_comparison.csv',
  protocolStatus = 'final',
  dataset,
  adaptationMethod,
  className,
  compact = false,
}) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const statusConfig: Record<
    ProtocolStatus,
    { label: string; bg: string; text: string; border: string; icon: React.ReactNode }
  > = {
    final: {
      label: 'Verified Final',
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      border: 'border-emerald-500/30',
      icon: <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />,
    },
    'diagnostic-only': {
      label: 'Diagnostic Only',
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      border: 'border-amber-500/30',
      icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />,
    },
    'demo-scale': {
      label: 'Demo Scale',
      bg: 'bg-cyan-500/10',
      text: 'text-cyan-400',
      border: 'border-cyan-500/30',
      icon: <Info className="w-3.5 h-3.5 text-cyan-400" />,
    },
    'requires verification': {
      label: 'Needs Verification',
      bg: 'bg-rose-500/10',
      text: 'text-rose-400',
      border: 'border-rose-500/30',
      icon: <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />,
    },
  };

  const cfg = statusConfig[protocolStatus] || statusConfig['final'];

  if (compact) {
    return (
      <span
        className={clsx(
          'inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full border',
          cfg.bg,
          cfg.text,
          cfg.border,
          className
        )}
        title={`Source: ${sourceFile}`}
      >
        {cfg.icon}
        <span>{cfg.label}</span>
      </span>
    );
  }

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className={clsx(
          'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-mono cursor-help transition-all duration-150',
          cfg.bg,
          cfg.text,
          cfg.border,
          className
        )}
      >
        {cfg.icon}
        <span className="font-semibold">{cfg.label}</span>
        <span className="text-slate-500">•</span>
        <span className="text-slate-400 truncate max-w-[140px]" title={sourceFile}>
          {sourceFile.split('/').pop()}
        </span>
      </div>

      {showTooltip && (
        <div className="absolute left-0 top-full mt-1.5 z-50 w-72 p-3 bg-slate-900 border border-slate-700/80 rounded-lg shadow-2xl text-xs text-slate-200 backdrop-blur-md animate-in fade-in duration-150">
          <div className="font-semibold text-slate-100 flex items-center justify-between pb-1.5 border-b border-slate-800 mb-2">
            <span>Data Provenance Metadata</span>
            <FileText className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="space-y-1.5 font-mono text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-400">Source:</span>
              <span className="text-cyan-300 font-medium truncate max-w-[180px]" title={sourceFile}>
                {sourceFile}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Protocol Status:</span>
              <span className={clsx('font-semibold', cfg.text)}>{cfg.label}</span>
            </div>
            {dataset && (
              <div className="flex justify-between">
                <span className="text-slate-400">Dataset:</span>
                <span className="text-slate-200">{dataset}</span>
              </div>
            )}
            {adaptationMethod && (
              <div className="flex justify-between">
                <span className="text-slate-400">Adaptation:</span>
                <span className="text-purple-300">{adaptationMethod}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
