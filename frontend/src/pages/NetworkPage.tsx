import React from 'react';
import Topology3D from '../components/topology/Topology3D';

export const NetworkPage: React.FC = () => {
  return (
    <div className="h-[calc(100vh-6.5rem)] w-full flex flex-col space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Network Topology</h1>
          <p className="text-xs font-mono text-text-secondary mt-0.5">
            ISOMETRIC 3D SMART-GRID ASSET TOPOLOGY & TRAFFIC FLOW MONITORING
          </p>
        </div>
      </div>

      <div className="flex-1 w-full rounded-xl overflow-hidden border border-border-muted relative glass-panel">
        <Topology3D />
      </div>
    </div>
  );
};

export default NetworkPage;
