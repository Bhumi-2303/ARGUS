import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { agents } from '../services/api';
import { Eye, Activity, Brain, ShieldAlert, FileText, ArrowRight, CornerDownLeft } from 'lucide-react';

const iconMap: Record<string, any> = {
  'ag-detect': Eye,
  'ag-assess': Activity,
  'ag-explain': Brain,
  'ag-respond': ShieldAlert,
  'ag-report': FileText,
};

const flowLabels = [
  "Detected Event",
  "Risk Score + Severity",
  "SHAP Evidence",
  "Recommended Action"
];

export default function Pipeline() {
  return (
    <div className="flex flex-col gap-6 h-full pb-10">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100">ARGUS Multi-Agent Pipeline</h1>
        <p className="text-slate-400 text-sm mt-1">How agents collaborate to detect, understand, prioritize and respond to cyber threats.</p>
      </div>

      <div className="glass-panel flex-1 flex flex-col p-8 relative overflow-x-auto min-h-[600px]">
        {/* Main Pipeline Container */}
        <div className="flex flex-col lg:flex-row items-center justify-between mt-20 relative w-full max-w-6xl mx-auto gap-12 lg:gap-0">
          
          {/* Dashed Feedback Arrow (SVG) */}
          <svg className="hidden lg:block absolute top-0 left-0 w-full h-full pointer-events-none z-0" style={{ minHeight: '300px' }}>
             {/* Main horizontal line for forward flows */}
             <line x1="10%" y1="40%" x2="90%" y2="40%" stroke="#334155" strokeWidth="3" />
             {/* Feedback Loop Line */}
             <path 
               d="M 85% 40% Q 85% 90% 50% 90% T 15% 40%" 
               fill="none" 
               stroke="#8b5cf6" 
               strokeWidth="2" 
               strokeDasharray="6 6" 
               className="animate-[dash_30s_linear_infinite]"
             />
             <polygon points="15%,40% 12%,45% 18%,45%" fill="#8b5cf6" transform="rotate(-15 15% 40%)" />
             <text x="50%" y="88%" fill="#8b5cf6" fontSize="12" fontWeight="bold" textAnchor="middle" className="uppercase tracking-wider">
               Feedback / Learning
             </text>
          </svg>

          {agents.map((agent, index) => {
            const Icon = iconMap[agent.id] || Eye;
            return (
              <React.Fragment key={agent.id}>
                {/* Agent Card */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative z-10 flex flex-col items-center w-full lg:w-48 group shrink-0"
                >
                  <Link to={`/pipeline/${agent.id}`} className="w-full">
                    <div className="bg-slate-900 border border-slate-700 hover:border-blue-500 hover:bg-slate-800 transition-all rounded-xl p-5 flex flex-col items-center text-center shadow-lg shadow-black/50 cursor-pointer">
                      <div className="relative mb-3">
                        <div className="p-3 bg-slate-800 rounded-lg group-hover:bg-slate-700 transition-colors">
                          <Icon className="w-8 h-8 text-blue-400 group-hover:text-blue-300" />
                        </div>
                        {agent.status === 'Active' && (
                          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-emerald-500 border-2 border-slate-900 rounded-full animate-pulse"></span>
                        )}
                      </div>
                      <h3 className="text-sm font-bold text-slate-200 mb-1">{agent.name}</h3>
                      <p className="text-xs text-slate-400 line-clamp-2">{agent.roleSummary}</p>
                    </div>
                  </Link>
                </motion.div>

                {/* Connecting Arrow with Label */}
                {index < agents.length - 1 && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.1 + 0.2 }}
                    className="flex lg:hidden flex-col items-center my-4 relative z-10"
                  >
                    <ArrowRight className="w-6 h-6 text-slate-500 rotate-90 lg:rotate-0 mb-1" />
                    <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wider bg-slate-900 px-2 py-1 rounded border border-slate-700">
                      {flowLabels[index]}
                    </span>
                  </motion.div>
                )}

                {/* Desktop Flow Label Overlays */}
                {index < agents.length - 1 && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.1 + 0.2 }}
                    className="hidden lg:flex absolute z-20 whitespace-nowrap"
                    style={{ left: `${18 + index * 20}%`, top: '35%', transform: 'translateX(-50%)' }}
                  >
                    <div className="flex flex-col items-center">
                      <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wider bg-slate-950 px-2 py-1 rounded-full border border-slate-700 shadow-md">
                        {flowLabels[index]}
                      </span>
                      <ArrowRight className="w-4 h-4 text-blue-500 mt-1" />
                    </div>
                  </motion.div>
                )}
              </React.Fragment>
            );
          })}

          {/* Final Audit Trail Output Arrow (Desktop) */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="hidden lg:flex absolute z-20 whitespace-nowrap"
            style={{ left: '95%', top: '35%', transform: 'translateX(-50%)' }}
          >
            <div className="flex flex-col items-center">
              <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider bg-slate-950 px-2 py-1 rounded-full border border-slate-700 shadow-md">
                Audit Trail
              </span>
              <ArrowRight className="w-4 h-4 text-emerald-500 mt-1" />
            </div>
          </motion.div>

        </div>
        
        {/* Helper styling for dash animation */}
        <style dangerouslySetInnerHTML={{__html: `
          @keyframes dash {
            to { stroke-dashoffset: -1000; }
          }
        `}} />
      </div>
    </div>
  );
}
