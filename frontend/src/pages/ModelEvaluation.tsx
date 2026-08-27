import React from 'react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';
import { models, crossDomainModels } from '../services/api';
import { ArrowRight, Database, BrainCircuit, ShieldAlert, AlertTriangle } from 'lucide-react';

// ==========================================
// EDITABLE CONSTANTS FOR REAL EXPERIMENTS
// ==========================================
const TRAINING_DOMAIN = "CICIoT2023";
const TESTING_DOMAIN = "NF-ToN-IoT";
const THRESHOLD_FPR = 0.05; // 5% False Positive Rate threshold
const THRESHOLD_F1 = 0.90;  // 90% F1 Score target

export default function ModelEvaluation() {
  // Format data for Recharts grouped bar chart
  const comparisonData = [
    { metric: 'Accuracy',   XGBoost: models[0].accuracy, LightGBM: models[1].accuracy, 'FT-Transformer': models[2].accuracy },
    { metric: 'Precision',  XGBoost: models[0].precision, LightGBM: models[1].precision, 'FT-Transformer': models[2].precision },
    { metric: 'Recall',     XGBoost: models[0].recall, LightGBM: models[1].recall, 'FT-Transformer': models[2].recall },
    { metric: 'F1 Score',   XGBoost: models[0].f1, LightGBM: models[1].f1, 'FT-Transformer': models[2].f1 },
    { metric: 'MCC',        XGBoost: models[0].mcc, LightGBM: models[1].mcc, 'FT-Transformer': models[2].mcc },
  ];

  // Helper to format radar chart data per model
  const getRadarData = (model: any) => [
    { subject: 'Accuracy', A: model.accuracy, fullMark: 1 },
    { subject: 'Precision', A: model.precision, fullMark: 1 },
    { subject: 'Recall', A: model.recall, fullMark: 1 },
    { subject: 'F1', A: model.f1, fullMark: 1 },
    { subject: 'MCC', A: model.mcc, fullMark: 1 },
  ];

  return (
    <div className="flex flex-col gap-8 pb-10">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100">ML Model Evaluation</h1>
        <p className="text-slate-400 text-sm mt-1">
          Performance metrics for the ARGUS ensemble. 
          <span className="ml-2 text-orange-400 font-medium bg-orange-400/10 px-2 py-0.5 rounded border border-orange-400/20 inline-flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            Demo values — not final experimental results
          </span>
        </p>
      </div>

      {/* Grouped Bar Chart Comparison */}
      <div className="glass-panel p-6">
        <h2 className="text-lg font-semibold text-slate-200 mb-6">Ensemble Comparison (In-Domain)</h2>
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparisonData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis dataKey="metric" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 1]} stroke="#94a3b8" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }}
                cursor={{ fill: '#1e293b' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="XGBoost" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="LightGBM" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="FT-Transformer" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Individual Model Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {models.map((model) => (
          <div key={model.id} className="glass-panel p-6 flex flex-col relative overflow-hidden">
            
            <div className="flex justify-between items-start mb-6">
              <h3 className="text-lg font-bold text-slate-100">{model.name}</h3>
              <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold bg-slate-900 px-2 py-1 rounded border border-slate-800">
                In-Domain
              </span>
            </div>

            {/* Radar Chart */}
            <div className="h-[200px] w-full -ml-4 mb-4">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={getRadarData(model)}>
                  <PolarGrid stroke="#334155" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 1]} tick={false} axisLine={false} />
                  <Radar name={model.name} dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Metric Grid */}
            <div className="grid grid-cols-2 gap-3 mt-auto">
              <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800/50">
                <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Accuracy</p>
                <p className="text-lg font-mono text-slate-200">{(model.accuracy * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800/50">
                <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">F1 Score</p>
                <p className={`text-lg font-mono ${model.f1 >= THRESHOLD_F1 ? 'text-emerald-400' : 'text-yellow-400'}`}>
                  {(model.f1 * 100).toFixed(1)}%
                </p>
              </div>
              <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800/50">
                <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">MCC</p>
                <p className="text-lg font-mono text-slate-200">{model.mcc.toFixed(3)}</p>
              </div>
              <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800/50">
                <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">FPR</p>
                <p className={`text-lg font-mono ${model.fpr <= THRESHOLD_FPR ? 'text-emerald-400' : 'text-red-400'}`}>
                  {(model.fpr * 100).toFixed(1)}%
                </p>
              </div>
            </div>
            
            <div className="mt-4 text-center">
              <span className="text-[10px] text-orange-500/70 font-medium">Demo values — not final experimental results</span>
            </div>
          </div>
        ))}
      </div>

      {/* Cross-Domain Evaluation Section */}
      <div className="glass-panel p-6 mt-4">
        <div className="flex items-center justify-between mb-8 border-b border-slate-800 pb-4">
          <h2 className="text-lg font-semibold text-slate-200">Cross-Domain Evaluation</h2>
          <span className="text-xs text-orange-400 bg-orange-400/10 px-3 py-1 rounded-full border border-orange-400/20 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" />
            Placeholder pending real experiment files
          </span>
        </div>

        {/* Flow Diagram */}
        <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8 mb-12">
          
          <div className="flex flex-col items-center gap-3">
            <div className="w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center shadow-lg shadow-blue-500/5">
              <Database className="w-8 h-8 text-blue-400" />
            </div>
            <div className="text-center">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Training Domain</p>
              <p className="text-sm font-medium text-slate-200">{TRAINING_DOMAIN}</p>
            </div>
          </div>

          <ArrowRight className="w-6 h-6 text-slate-600 rotate-90 md:rotate-0" />

          <div className="flex flex-col items-center gap-3">
            <div className="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center shadow-lg shadow-purple-500/5 relative">
              <BrainCircuit className="w-8 h-8 text-purple-400" />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-purple-500"></span>
              </span>
            </div>
            <div className="text-center">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">ARGUS Ensemble</p>
              <p className="text-sm font-medium text-slate-200">Zero-Shot Transfer</p>
            </div>
          </div>

          <ArrowRight className="w-6 h-6 text-slate-600 rotate-90 md:rotate-0" />

          <div className="flex flex-col items-center gap-3">
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center shadow-lg shadow-emerald-500/5">
              <ShieldAlert className="w-8 h-8 text-emerald-400" />
            </div>
            <div className="text-center">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Testing Domain</p>
              <p className="text-sm font-medium text-slate-200">{TESTING_DOMAIN}</p>
            </div>
          </div>

        </div>

        {/* Metrics Table */}
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/80 text-xs uppercase font-bold text-slate-500 border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Model</th>
                <th className="px-6 py-4">Accuracy</th>
                <th className="px-6 py-4">Precision</th>
                <th className="px-6 py-4">Recall</th>
                <th className="px-6 py-4">F1 Score</th>
                <th className="px-6 py-4">MCC</th>
                <th className="px-6 py-4">FPR</th>
                <th className="px-6 py-4">FNR</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 bg-slate-900/30">
              {crossDomainModels.map((model) => (
                <tr key={model.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-200">{model.name.replace(' (Cross-Domain)', '')}</td>
                  <td className="px-6 py-4 font-mono">{(model.accuracy * 100).toFixed(1)}%</td>
                  <td className="px-6 py-4 font-mono">{(model.precision * 100).toFixed(1)}%</td>
                  <td className="px-6 py-4 font-mono">{(model.recall * 100).toFixed(1)}%</td>
                  <td className="px-6 py-4 font-mono">
                    <span className={model.f1 >= THRESHOLD_F1 ? 'text-emerald-400' : 'text-slate-300'}>
                      {(model.f1 * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono">{model.mcc.toFixed(3)}</td>
                  <td className="px-6 py-4 font-mono">
                    <span className={model.fpr <= THRESHOLD_FPR ? 'text-emerald-400' : 'text-orange-400'}>
                      {(model.fpr * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono">{(model.fnr * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
}
