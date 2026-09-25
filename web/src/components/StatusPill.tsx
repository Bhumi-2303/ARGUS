import React from 'react';
import { clsx } from 'clsx';

export type StatusVariant =
  | 'healthy'
  | 'ready'
  | 'connected'
  | 'warning'
  | 'degraded'
  | 'reconnecting'
  | 'error'
  | 'failed'
  | 'offline'
  | 'native'
  | 'coral_aligned'
  | 'dann_adapted'
  | 'info';

export interface StatusPillProps {
  status: StatusVariant | string;
  label?: string;
  pulse?: boolean;
  className?: string;
}

export const StatusPill: React.FC<StatusPillProps> = ({
  status,
  label,
  pulse = true,
  className,
}) => {
  const normStatus = String(status).toLowerCase();

  const styles: Record<string, { bg: string; text: string; border: string; dot: string }> = {
    healthy: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' },
    ready: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' },
    connected: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' },
    warning: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30', dot: 'bg-amber-400' },
    degraded: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30', dot: 'bg-amber-400' },
    reconnecting: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30', dot: 'bg-amber-400' },
    error: { bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/30', dot: 'bg-rose-400' },
    failed: { bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/30', dot: 'bg-rose-400' },
    offline: { bg: 'bg-slate-800', text: 'text-slate-400', border: 'border-slate-700', dot: 'bg-slate-400' },
    native: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/30', dot: 'bg-blue-400' },
    coral_aligned: { bg: 'bg-purple-500/10', text: 'text-purple-400', border: 'border-purple-500/30', dot: 'bg-purple-400' },
    dann_adapted: { bg: 'bg-cyan-500/10', text: 'text-cyan-400', border: 'border-cyan-500/30', dot: 'bg-cyan-400' },
    info: { bg: 'bg-sky-500/10', text: 'text-sky-400', border: 'border-sky-500/30', dot: 'bg-sky-400' },
  };

  const st = styles[normStatus] || styles['info'];
  const displayLabel = label || status;

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-xs font-mono font-medium',
        st.bg,
        st.text,
        st.border,
        className
      )}
    >
      <span className="relative flex h-2 w-2">
        {pulse && (
          <span
            className={clsx(
              'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
              st.dot
            )}
          />
        )}
        <span className={clsx('relative inline-flex rounded-full h-2 w-2', st.dot)} />
      </span>
      <span>{displayLabel}</span>
    </span>
  );
};
