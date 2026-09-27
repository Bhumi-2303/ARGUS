import React, { useState, Suspense } from 'react';
import { Card } from '../../components/Card';
import ModelComparisonPage from '../benchmark/ModelComparisonPage';
import DomainShiftPage from '../shift/DomainShiftPage';
import ProtocolLimitsPage from '../protocol_limits/ProtocolLimitsPage';

export default function ResultsPage() {
  const [activeTab, setActiveTab] = useState<'benchmark' | 'shift' | 'limits'>('benchmark');

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900 dark:text-white">
          Results & Evaluation Overview
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Verified experimental evaluation results, domain shift analysis, and protocol limitations. 
          All metrics reflect bit-for-bit reproducible outcomes from the frozen test partitions.
        </p>
      </div>

      <div className="flex border-b border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setActiveTab('benchmark')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'benchmark'
              ? 'border-cyan-500 text-cyan-600 dark:text-cyan-400'
              : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
          }`}
        >
          Classification Metrics
        </button>
        <button
          onClick={() => setActiveTab('shift')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'shift'
              ? 'border-cyan-500 text-cyan-600 dark:text-cyan-400'
              : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
          }`}
        >
          Domain Shift
        </button>
        <button
          onClick={() => setActiveTab('limits')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'limits'
              ? 'border-cyan-500 text-cyan-600 dark:text-cyan-400'
              : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
          }`}
        >
          Protocol & Limits
        </button>
      </div>

      <div className="mt-6">
        <Suspense fallback={<div className="p-8 text-center text-slate-500">Loading results...</div>}>
          {activeTab === 'benchmark' && <ModelComparisonPage />}
          {activeTab === 'shift' && <DomainShiftPage />}
          {activeTab === 'limits' && <ProtocolLimitsPage />}
        </Suspense>
      </div>
    </div>
  );
}
