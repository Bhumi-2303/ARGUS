import React from 'react';
import { Info } from 'lucide-react';

export const MetricInfoIcon: React.FC<{ metric: 'balanced_acc' | 'specificity' | 'recall' }> = ({ metric }) => {
  const tooltips = {
    balanced_acc: "Averages accuracy across both classes equally; prevents a 99% attack dataset from falsely inflating the score to 99% when the model just guesses 'Attack' every time.",
    specificity: "True Negative Rate (1 - FPR). Crucial for avoiding alert fatigue; measures how well the model avoids flagging benign traffic as malicious.",
    recall: "True Positive Rate. Measures how many of the actual attacks were successfully detected."
  };

  return (
    <div className="inline-flex group relative ml-1.5 cursor-help" title={tooltips[metric]}>
      <Info className="w-3 h-3 text-slate-500 hover:text-cyan-400 transition-colors" />
      <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-48 p-2 bg-slate-800 text-slate-200 text-[10px] rounded shadow-xl border border-slate-700 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
        {tooltips[metric]}
      </div>
    </div>
  );
};
