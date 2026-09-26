import React, { useState, useEffect } from 'react';
import { Search, Network } from 'lucide-react';
import Topology3D from '../components/topology/Topology3D';
import { NetworkNode } from '../types';
import { getNetworkNodes } from '../services/api';
import { STATUS_COLORS } from '../components/topology/Node3DModel';

export const NetworkPage: React.FC = () => {
  const [nodes, setNodes] = useState<NetworkNode[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | undefined>(undefined);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  useEffect(() => {
    let mounted = true;
    async function loadNodes() {
      try {
        const data = await getNetworkNodes();
        if (mounted) {
          setNodes(data);
        }
      } catch (err) {
        console.error('Failed to load network nodes:', err);
      }
    }
    loadNodes();

    return () => {
      mounted = false;
    };
  }, []);

  const filteredNodes = nodes.filter((node) => {
    const matchesSearch =
      node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      node.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      node.type.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'all' || node.status === statusFilter;
    const matchesType = typeFilter === 'all' || node.type === typeFilter;

    return matchesSearch && matchesStatus && matchesType;
  });

  return (
    <div className="h-[calc(100vh-6.5rem)] w-full flex flex-col space-y-3 select-none">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Network Topology & Grid Map</h1>
          <p className="text-xs font-mono text-text-secondary mt-0.5">
            SPATIAL ISOMETRIC 3D GRID INSPECTOR & FILTERABLE ASSET DIRECTORY
          </p>
        </div>
      </div>

      {/* Main 2-Column Split: Persistent Side Panel + 3D Canvas */}
      <div className="flex-1 w-full flex flex-col lg:flex-row gap-4 overflow-hidden min-h-0">
        {/* Persistent Left Node Directory Side Panel */}
        <div className="w-full lg:w-80 flex-shrink-0 glass-panel p-4 flex flex-col space-y-3 overflow-hidden border border-border-muted">
          <div className="flex items-center justify-between border-b border-border-muted pb-2">
            <span className="text-xs font-mono font-bold tracking-wider text-text-secondary uppercase flex items-center gap-1.5">
              <Network className="w-4 h-4 text-info" /> GRID ASSET DIRECTORY ({filteredNodes.length})
            </span>
          </div>

          {/* Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search asset by name, ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-bg-surface border border-border-muted text-xs text-text-primary placeholder:text-text-secondary focus:outline-none focus:border-info"
            />
          </div>

          {/* Status & Type Select Filters */}
          <div className="grid grid-cols-2 gap-2">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-2 py-1.5 rounded-lg bg-bg-surface border border-border-muted text-[11px] font-mono text-text-primary focus:outline-none focus:border-info"
            >
              <option value="all">All Statuses</option>
              <option value="secure">Secure</option>
              <option value="protected">Protected</option>
              <option value="at-risk">At Risk</option>
              <option value="compromised">Compromised</option>
            </select>

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-2 py-1.5 rounded-lg bg-bg-surface border border-border-muted text-[11px] font-mono text-text-primary focus:outline-none focus:border-info"
            >
              <option value="all">All Types</option>
              <option value="substation">Substation</option>
              <option value="scada">SCADA</option>
              <option value="rtu">RTU</option>
              <option value="plc">PLC</option>
              <option value="ied">IED</option>
              <option value="hmi">HMI</option>
              <option value="iot-sensor">Sensor</option>
            </select>
          </div>

          {/* Scrollable Node List */}
          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {filteredNodes.map((node) => {
              const statusStyle = STATUS_COLORS[node.status] || STATUS_COLORS.secure;
              const isSelected = selectedNodeId === node.id;

              return (
                <button
                  key={node.id}
                  onClick={() => setSelectedNodeId(node.id)}
                  className={`w-full text-left p-2.5 rounded-lg border transition-all flex items-center justify-between group ${
                    isSelected
                      ? 'bg-info/15 border-info text-info ring-1 ring-info/50'
                      : 'bg-bg-surface border-border-muted/60 hover:bg-bg-surface-raised/80 hover:border-info/40'
                  }`}
                >
                  <div className="space-y-0.5 truncate">
                    <div className="text-xs font-semibold text-text-primary truncate group-hover:text-info">
                      {node.name}
                    </div>
                    <div className="flex items-center gap-2 font-mono text-[10px] text-text-secondary">
                      <span>{node.id}</span>
                      <span>•</span>
                      <span className="uppercase">{node.type}</span>
                    </div>
                  </div>

                  <span
                    className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${statusStyle.glowClass}`}
                    style={{ backgroundColor: statusStyle.color }}
                    title={`Status: ${node.status}`}
                  />
                </button>
              );
            })}

            {filteredNodes.length === 0 && (
              <div className="p-6 text-center text-text-secondary text-xs font-mono">
                No matching assets found.
              </div>
            )}
          </div>
        </div>

        {/* 3D Topology Area */}
        <div className="flex-1 w-full rounded-xl overflow-hidden border border-border-muted relative glass-panel min-h-[400px]">
          <Topology3D
            key={selectedNodeId || 'default'}
            initialSelectedNodeId={selectedNodeId}
          />
        </div>
      </div>
    </div>
  );
};

export default NetworkPage;
