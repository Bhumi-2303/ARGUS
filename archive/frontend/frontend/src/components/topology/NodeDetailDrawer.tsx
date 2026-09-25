import React from 'react';
import { X, ShieldAlert, Cpu, Activity, Clock, Link as LinkIcon, AlertTriangle } from 'lucide-react';
import { NetworkNode } from '../../types';
import { STATUS_COLORS } from './Node3DModel';

interface DrawerProps {
  node: NetworkNode | null;
  allNodes: NetworkNode[];
  onClose: () => void;
  onSelectNode: (node: NetworkNode) => void;
}

export const NodeDetailDrawer: React.FC<DrawerProps> = ({
  node,
  allNodes,
  onClose,
  onSelectNode
}) => {
  if (!node) return null;

  const statusStyle = STATUS_COLORS[node.status] || STATUS_COLORS.secure;

  // Find connected node objects
  const connectedNodeObjects = node.connectedAssets
    .map((id) => allNodes.find((n) => n.id === id))
    .filter((n): n is NetworkNode => Boolean(n));

  return (
    <div className="absolute top-4 right-4 bottom-4 w-96 max-w-[calc(100vw-2rem)] glass-panel-raised p-6 flex flex-col z-30 shadow-2xl overflow-y-auto animate-in slide-in-from-right duration-200">
      {/* Header & Close Button */}
      <div className="flex items-start justify-between border-b border-border-muted pb-4">
        <div>
          <span className="text-[10px] font-mono font-bold tracking-widest text-text-secondary uppercase">
            ASSET DETAIL INSPECTOR
          </span>
          <h2 className="text-xl font-bold text-text-primary mt-1 tracking-tight">
            {node.name}
          </h2>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg bg-bg-surface border border-border-muted text-text-secondary hover:text-text-primary transition-colors"
          aria-label="Close detail panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body Details */}
      <div className="flex-1 py-4 space-y-5">
        {/* Status & Risk KPI Badge */}
        <div className="grid grid-cols-2 gap-3">
          <div className={`p-3 rounded-lg border ${statusStyle.borderClass} ${statusStyle.bgClass}`}>
            <span className="text-[10px] font-mono tracking-wider uppercase block opacity-80">
              STATUS
            </span>
            <span className="text-sm font-bold uppercase tracking-wide mt-0.5 block" style={{ color: statusStyle.color }}>
              {node.status}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-bg-surface border border-border-muted">
            <span className="text-[10px] font-mono tracking-wider text-text-secondary uppercase block">
              RISK SCORE
            </span>
            <div className="flex items-center gap-2 mt-0.5">
              <span className={`text-lg font-bold font-mono ${node.riskScore > 70 ? 'text-critical' : node.riskScore > 40 ? 'text-warn' : 'text-safe'}`}>
                {node.riskScore}/100
              </span>
            </div>
          </div>
        </div>

        {/* Current Threat (if present) */}
        {node.currentThreat && (
          <div className="p-3 rounded-lg bg-critical/10 border border-critical/40 glow-critical">
            <div className="flex items-center gap-2 text-critical font-bold text-xs uppercase tracking-wider">
              <AlertTriangle className="w-4 h-4 animate-pulse" />
              <span>Active Threat Detected</span>
            </div>
            <p className="text-xs text-text-primary mt-1.5 font-medium leading-relaxed">
              {node.currentThreat}
            </p>
          </div>
        )}

        {/* Asset Properties Table */}
        <div className="space-y-3 bg-bg-surface p-4 rounded-lg border border-border-muted text-xs">
          <div className="flex justify-between items-center py-1 border-b border-border-muted/50">
            <span className="text-text-secondary flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-info" /> ASSET TYPE
            </span>
            <span className="font-mono text-text-primary uppercase font-medium">{node.type}</span>
          </div>

          <div className="flex justify-between items-center py-1 border-b border-border-muted/50">
            <span className="text-text-secondary flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-info" /> ASSET ID
            </span>
            <span className="font-mono text-text-primary font-medium">{node.id}</span>
          </div>

          <div className="flex justify-between items-center py-1 border-b border-border-muted/50">
            <span className="text-text-secondary flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-info" /> LAST ACTIVITY
            </span>
            <span className="font-mono text-text-primary text-[11px]">
              {new Date(node.lastActivity).toLocaleTimeString()}
            </span>
          </div>

          <div className="flex justify-between items-center py-1">
            <span className="text-text-secondary flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-info" /> 3D POSITION
            </span>
            <span className="font-mono text-text-primary text-[11px]">
              X:{node.position.x} Y:{node.position.y} Z:{node.position.z}
            </span>
          </div>
        </div>

        {/* Connected Assets Chips */}
        <div>
          <span className="text-xs font-mono font-bold tracking-wider text-text-secondary uppercase flex items-center gap-1.5 mb-2">
            <LinkIcon className="w-3.5 h-3.5 text-info" /> CONNECTED ASSETS ({connectedNodeObjects.length})
          </span>
          <div className="flex flex-wrap gap-2">
            {connectedNodeObjects.map((connNode) => {
              const connStatusStyle = STATUS_COLORS[connNode.status] || STATUS_COLORS.secure;
              return (
                <button
                  key={connNode.id}
                  onClick={() => onSelectNode(connNode)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium border transition-all flex items-center gap-1.5 hover:scale-105 ${connStatusStyle.borderClass} ${connStatusStyle.bgClass}`}
                >
                  <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: connStatusStyle.color }} />
                  <span className="text-text-primary">{connNode.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NodeDetailDrawer;
