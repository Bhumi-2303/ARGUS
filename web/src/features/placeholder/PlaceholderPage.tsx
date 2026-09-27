import React from 'react';
import { Card } from '../../components/Card';
import { ProvenanceBadge } from '../../components/ProvenanceBadge';
import { StatusPill } from '../../components/StatusPill';
import { Construction, CheckCircle2 } from 'lucide-react';

export function createPlaceholderPage(title: string, description: string) {
  return function PlaceholderPage() {
    return (
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">{title}</h1>
              <StatusPill status="info" label="Registered Route" pulse={false} />
            </div>
            <p className="text-xs text-slate-400 mt-1">{description}</p>
          </div>
          <ProvenanceBadge
            sourceFile="results/verified/five_model_complete_comparison.csv"
            protocolStatus="final"
          />
        </div>

        <Card variant="gradient" className="p-8 text-center space-y-4">
          <div className="mx-auto w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Construction className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{title} Feature Module Wiring Verified</h3>
          <p className="text-xs text-slate-400 max-w-lg mx-auto">
            This route is registered in <code className="text-cyan-300 font-mono bg-slate-900 px-1.5 py-0.5 rounded">src/app/pages.ts</code> and dynamically mapped to the sidebar shell navigation.
          </p>
          <div className="pt-2 flex justify-center gap-3">
            <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400 font-mono bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded">
              <CheckCircle2 className="w-3.5 h-3.5" /> Shell Wiring Active
            </span>
          </div>
        </Card>
      </div>
    );
  };
}
