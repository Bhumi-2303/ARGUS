import React from 'react';
import { BarChart2 } from 'lucide-react';

const Analytics: React.FC = () => {
  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight">Security Analytics</h1>
        <p className="text-slate-400 text-sm mt-1">Detector performance and domain adaptation metrics</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
          <div className="text-slate-400 text-xs font-semibold mb-1">GLOBAL F1 SCORE</div>
          <div className="text-3xl font-bold text-slate-100">0.942</div>
          <div className="text-green-400 text-xs font-mono mt-2">+0.012 vs baseline</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
          <div className="text-slate-400 text-xs font-semibold mb-1">MATTHEWS CC (MCC)</div>
          <div className="text-3xl font-bold text-slate-100">0.915</div>
          <div className="text-green-400 text-xs font-mono mt-2">+0.024 vs baseline</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
          <div className="text-slate-400 text-xs font-semibold mb-1">FALSE POSITIVE RATE</div>
          <div className="text-3xl font-bold text-slate-100">0.021</div>
          <div className="text-amber-400 text-xs font-mono mt-2">Target &lt; 0.05</div>
        </div>
      </div>
      
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-8 text-center text-slate-500">
        <BarChart2 className="w-12 h-12 mx-auto mb-4 opacity-30" />
        <h3 className="text-lg font-medium text-slate-300 mb-2">Cross-Domain Performance Metrics</h3>
        <p className="max-w-md mx-auto text-sm">Detailed ROC-AUC and Domain Adaptation metrics are tracked in the research tracking system. This operational view will display live model drift when enough real-world data is collected.</p>
      </div>
    </div>
  );
};

export default Analytics;
