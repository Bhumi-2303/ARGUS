import React, { useState } from 'react';
import { Search, Cpu, AlertTriangle } from 'lucide-react';
import { NetworkNode } from '../../types';
import { STATUS_COLORS } from './Node3DModel';

interface NodeListViewProps {
  nodes: NetworkNode[];
  selectedNode: NetworkNode | null;
  onSelectNode: (node: NetworkNode) => void;
}

export const NodeListView: React.FC<NodeListViewProps> = ({
  nodes,
  selectedNode,
  onSelectNode
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filteredNodes = nodes.filter((node) => {
    const matchesSearch =
      node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      node.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      node.id.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'all' || node.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="w-full h-full bg-bg-void p-6 overflow-y-auto space-y-4">
      {/* Controls Bar */}
      <div className="flex flex-col sm:flex-row gap-3 justify-between items-stretch sm:items-center">
        {/* Search Bar */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search nodes by name, ID, or type..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-bg-surface border border-border-muted text-xs text-text-primary placeholder:text-text-secondary focus:outline-none focus:border-info"
          />
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-text-secondary">FILTER:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-bg-surface border border-border-muted text-xs text-text-primary focus:outline-none focus:border-info"
          >
            <option value="all">All Statuses ({nodes.length})</option>
            <option value="secure">Secure</option>
            <option value="protected">Protected</option>
            <option value="at-risk">At Risk</option>
            <option value="compromised">Compromised</option>
          </select>
        </div>
      </div>

      {/* Node Table */}
      <div className="glass-panel overflow-hidden border border-border-muted rounded-xl">
        <table className="w-full text-left text-xs text-text-primary">
          <thead className="bg-bg-surface-raised border-b border-border-muted font-mono text-[11px] text-text-secondary uppercase">
            <tr>
              <th className="p-3.5">Asset Name & ID</th>
              <th className="p-3.5">Type</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5">Risk Score</th>
              <th className="p-3.5">Active Threat</th>
              <th className="p-3.5">Connected Assets</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border-muted/50">
            {filteredNodes.map((node) => {
              const statusStyle = STATUS_COLORS[node.status] || STATUS_COLORS.secure;
              const isSelected = selectedNode?.id === node.id;

              return (
                <tr
                  key={node.id}
                  onClick={() => onSelectNode(node)}
                  className={`cursor-pointer transition-colors hover:bg-bg-surface-raised/60 ${
                    isSelected ? 'bg-info/10' : ''
                  }`}
                >
                  {/* Asset Name */}
                  <td className="p-3.5 font-medium">
                    <div className="font-semibold text-text-primary">{node.name}</div>
                    <div className="font-mono text-[10px] text-text-secondary">{node.id}</div>
                  </td>

                  {/* Type */}
                  <td className="p-3.5">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-bg-surface-raised border border-border-muted font-mono text-[11px] uppercase">
                      <Cpu className="w-3 h-3 text-info" /> {node.type}
                    </span>
                  </td>

                  {/* Status */}
                  <td className="p-3.5">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold uppercase border ${statusStyle.borderClass} ${statusStyle.bgClass}`}
                    >
                      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: statusStyle.color }} />
                      {node.status}
                    </span>
                  </td>

                  {/* Risk Score */}
                  <td className="p-3.5 font-mono font-bold">
                    <span className={node.riskScore > 70 ? 'text-critical' : node.riskScore > 40 ? 'text-warn' : 'text-safe'}>
                      {node.riskScore}/100
                    </span>
                  </td>

                  {/* Active Threat */}
                  <td className="p-3.5">
                    {node.currentThreat ? (
                      <span className="inline-flex items-center gap-1 text-critical font-medium">
                        <AlertTriangle className="w-3.5 h-3.5" /> {node.currentThreat}
                      </span>
                    ) : (
                      <span className="text-text-secondary/60 font-mono">None</span>
                    )}
                  </td>

                  {/* Connected Assets */}
                  <td className="p-3.5 font-mono text-[11px] text-text-secondary">
                    {node.connectedAssets.length} Connections
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredNodes.length === 0 && (
          <div className="p-8 text-center text-text-secondary text-xs font-mono">
            No network nodes matched the search query or status filter.
          </div>
        )}
      </div>
    </div>
  );
};

export default NodeListView;
