import React from 'react';

export default function Topology3D() {
  return (
    <div className="w-full h-full min-h-[400px] flex items-center justify-center bg-slate-900/50 rounded-lg border border-slate-700/50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-3"></div>
        <p className="text-slate-400 font-medium">Topology loading</p>
      </div>
    </div>
  );
}
