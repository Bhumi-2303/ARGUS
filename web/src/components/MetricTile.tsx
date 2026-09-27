import React from 'react';
import { Card } from './Card';
import { ProvenanceBadge, ProtocolStatus } from './ProvenanceBadge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { clsx } from 'clsx';

export interface MetricTileProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: number; // e.g. +14.2%
  changeLabel?: string;
  icon?: React.ReactNode;
  sourceFile?: string;
  protocolStatus?: ProtocolStatus;
  variant?: 'default' | 'glass' | 'gradient';
  className?: string;
}

export const MetricTile: React.FC<MetricTileProps> = ({
  title,
  value,
  subtitle,
  change,
  changeLabel,
  icon,
  sourceFile,
  protocolStatus = 'final',
  variant = 'default',
  className,
}) => {
  return (
    <Card variant={variant} className={clsx('relative overflow-hidden', className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">{title}</p>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono tracking-tight text-slate-900 dark:text-slate-100">{value}</span>
            {change !== undefined && (
              <span
                className={clsx(
                  'inline-flex items-center text-xs font-semibold px-1.5 py-0.5 rounded',
                  change > 0
                    ? 'text-emerald-400 bg-emerald-500/10'
                    : change < 0
                    ? 'text-rose-400 bg-rose-500/10'
                    : 'text-slate-500 dark:text-slate-400 bg-slate-200 dark:bg-slate-800'
                )}
              >
                {change > 0 ? (
                  <TrendingUp className="w-3 h-3 mr-0.5" />
                ) : change < 0 ? (
                  <TrendingDown className="w-3 h-3 mr-0.5" />
                ) : (
                  <Minus className="w-3 h-3 mr-0.5" />
                )}
                {change > 0 ? `+${change}%` : `${change}%`}
              </span>
            )}
          </div>
          {subtitle && <p className="text-xs text-slate-500 dark:text-slate-400">{subtitle}</p>}
        </div>
        {icon && <div className="p-2.5 rounded-lg bg-slate-100 dark:bg-slate-200 dark:bg-slate-800/80 text-cyan-600 dark:text-cyan-400 border border-slate-200 dark:border-slate-700/50">{icon}</div>}
      </div>

      {sourceFile && (
        <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800/80 flex items-center justify-between">
          <ProvenanceBadge sourceFile={sourceFile} protocolStatus={protocolStatus} compact />
          {changeLabel && <span className="text-[11px] text-slate-500">{changeLabel}</span>}
        </div>
      )}
    </Card>
  );
};
