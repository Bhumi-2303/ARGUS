import React from 'react';

export const LegendOverlay: React.FC = () => {
  return (
    <div className="absolute bottom-4 left-4 z-10 glass-panel p-3.5 text-xs space-y-3 select-none pointer-events-auto border border-border-muted max-w-xs shadow-xl">
      <div className="text-[10px] font-mono font-bold tracking-widest text-text-secondary uppercase border-b border-border-muted/60 pb-1.5">
        GRID TOPOLOGY LEGEND
      </div>

      {/* Node Status Keys */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-2">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-info glow-info" />
          <span className="text-text-primary text-[11px]">Secure</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-safe glow-safe" />
          <span className="text-text-primary text-[11px]">Protected</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-warn glow-warn" />
          <span className="text-text-primary text-[11px]">At Risk</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-critical glow-critical animate-pulse" />
          <span className="text-text-primary text-[11px]">Compromised</span>
        </div>
      </div>

      {/* Connection Traffic Keys */}
      <div className="border-t border-border-muted/60 pt-2 space-y-1.5">
        <div className="flex items-center justify-between text-[11px]">
          <span className="text-text-secondary">Normal Traffic:</span>
          <div className="flex items-center gap-1.5">
            <span className="w-8 h-0.5 bg-info" />
            <span className="text-info font-mono text-[10px]">Solid Cyan</span>
          </div>
        </div>
        <div className="flex items-center justify-between text-[11px]">
          <span className="text-text-secondary">Suspicious Traffic:</span>
          <div className="flex items-center gap-1.5">
            <span className="w-8 h-0.5 bg-critical border-b border-dashed border-critical animate-pulse" />
            <span className="text-critical font-mono text-[10px]">Flowing Red</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LegendOverlay;
