with open("web/src/features/monitor/LiveMonitorPage.tsx", "r") as f:
    content = f.read()

# Add configuration for MIN_N
if "const MIN_TOTAL_N" not in content:
    content = content.replace(
        "export default function LiveMonitorPage() {",
        "const MIN_TOTAL_N = 50;\nconst MIN_CLASS_N = 5;\n\nexport default function LiveMonitorPage() {"
    )

old_card = """          const stats = modelStats[mId] || { tp: 0, fp: 0, tn: 0, fn: 0 };
          const recall =
            stats.tp + stats.fn > 0 ? stats.tp / (stats.tp + stats.fn) : 0;
          const specificity =
            stats.tn + stats.fp > 0 ? stats.tn / (stats.tn + stats.fp) : 0;
          const balancedAcc = (recall + specificity) / 2;

          return (
            <Card key={mId} className="space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-bold font-mono text-cyan-300 truncate max-w-[140px]" title={mId}>
                  {mId}
                </span>
                <ProvenanceBadge
                  sourceFile="results/verified/five_model_complete_comparison.csv"
                  protocolStatus="final"
                  compact
                />
              </div>

              <div className="space-y-2 font-mono text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Balanced Acc:</span>
                  <span className="text-emerald-400 font-extrabold text-sm">
                    {(balancedAcc * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Specificity (1-FPR):</span>
                  <span className="text-cyan-400 font-bold">
                    {(specificity * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Recall (TPR):</span>
                  <span className="text-blue-400 font-bold">
                    {(recall * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              <div className="text-[10px] font-mono text-slate-500 pt-2 border-t border-slate-800/60 flex justify-between">
                <span>TP: {stats.tp} | TN: {stats.tn}</span>
                <span>FP: {stats.fp} | FN: {stats.fn}</span>
              </div>
            </Card>
          );"""

new_card = """          const stats = modelStats[mId] || { tp: 0, fp: 0, tn: 0, fn: 0 };
          const n_pos = stats.tp + stats.fn;
          const n_neg = stats.tn + stats.fp;
          const total_n = n_pos + n_neg;
          
          const isWarmingUp = total_n < MIN_TOTAL_N || n_pos < MIN_CLASS_N || n_neg < MIN_CLASS_N;
          
          const recall = n_pos > 0 ? stats.tp / n_pos : 0;
          const specificity = n_neg > 0 ? stats.tn / n_neg : 0;
          const balancedAcc = (recall + specificity) / 2;

          return (
            <Card key={mId} className="space-y-3 relative overflow-hidden data-card">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-bold font-mono text-cyan-300 truncate max-w-[140px]" title={mId}>
                  {mId}
                </span>
                <ProvenanceBadge
                  sourceFile="results/verified/five_model_complete_comparison.csv"
                  protocolStatus="final"
                  compact
                />
              </div>

              <div className="space-y-3 font-mono text-xs pb-1">
                <div className="flex flex-col gap-0.5">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Balanced Acc:</span>
                    {isWarmingUp ? (
                      <span className="text-slate-500 animate-pulse">--.-%</span>
                    ) : (
                      <span className="text-emerald-400 font-extrabold text-sm">
                        {(balancedAcc * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  {!isWarmingUp && <div className="text-[9px] text-right text-slate-500">(n={total_n}, {n_pos} atk / {n_neg} ben)</div>}
                </div>

                <div className="flex flex-col gap-0.5">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Specificity:</span>
                    {isWarmingUp ? (
                      <span className="text-slate-500 animate-pulse">--.-%</span>
                    ) : (
                      <span className="text-cyan-400 font-bold">
                        {(specificity * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  {!isWarmingUp && <div className="text-[9px] text-right text-slate-500">(n={n_neg} benign)</div>}
                </div>

                <div className="flex flex-col gap-0.5">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Recall:</span>
                    {isWarmingUp ? (
                      <span className="text-slate-500 animate-pulse">--.-%</span>
                    ) : (
                      <span className="text-blue-400 font-bold">
                        {(recall * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  {!isWarmingUp && <div className="text-[9px] text-right text-slate-500">(n={n_pos} attack)</div>}
                </div>
              </div>

              {isWarmingUp && (
                <div className="absolute inset-0 top-10 bg-slate-950/80 backdrop-blur-[1px] flex flex-col items-center justify-center z-10 p-2">
                  <div className="flex items-center gap-2 text-amber-500/90 mb-1">
                    <div className="w-2 h-2 rounded-full bg-amber-500 animate-ping"></div>
                    <span className="text-xs font-bold font-mono">WARMING UP</span>
                  </div>
                  <div className="text-[9px] text-slate-400 text-center font-mono leading-tight">
                    Requires {MIN_TOTAL_N} total events<br/>
                    and {MIN_CLASS_N} of each class.
                  </div>
                  <div className="text-[9px] text-cyan-400/80 mt-1 font-mono">
                    (n={total_n}, {n_pos} atk / {n_neg} ben)
                  </div>
                </div>
              )}

              <div className="text-[10px] font-mono text-slate-500 pt-2 border-t border-slate-800/60 flex justify-between">
                <span>TP: {stats.tp} | TN: {stats.tn}</span>
                <span>FP: {stats.fp} | FN: {stats.fn}</span>
              </div>
            </Card>
          );"""

content = content.replace(old_card, new_card)

with open("web/src/features/monitor/LiveMonitorPage.tsx", "w") as f:
    f.write(content)
