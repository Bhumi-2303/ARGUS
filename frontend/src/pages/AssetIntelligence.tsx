import React, { useEffect, useState } from 'react';
import { Server } from 'lucide-react';
import { fetchIncidents } from '../services/api';

const AssetIntelligence: React.FC = () => {
  const [assets, setAssets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAssets = async () => {
      try {
        const incidents = await fetchIncidents();
        const assetMap = new Map<string, any>();
        
        incidents.forEach(inc => {
          if (!assetMap.has(inc.asset)) {
            assetMap.set(inc.asset, {
              id: inc.asset,
              type: inc.asset.includes('MTU') || inc.asset.includes('SCADA') ? 'SCADA Master' : 
                    inc.asset.includes('RTU') || inc.asset.includes('PLC') ? 'Field Controller' : 'Network Device',
              criticality: inc.asset_criticality || Math.floor(Math.random() * 3) + 3,
              currentRisk: 0,
              incidents: 0
            });
          }
          const asset = assetMap.get(inc.asset);
          asset.incidents += 1;
          asset.currentRisk = Math.max(asset.currentRisk, inc.risk_score || 0);
        });
        
        setAssets(Array.from(assetMap.values()).sort((a, b) => b.currentRisk - a.currentRisk));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadAssets();
  }, []);

  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight">Asset Intelligence</h1>
        <p className="text-slate-400 text-sm mt-1">Grid infrastructure risk posture</p>
      </header>

      {loading ? (
        <div className="text-slate-400 font-mono animate-pulse">LOADING ASSET DATA...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {assets.map(asset => (
            <div key={asset.id} className="bg-slate-900 border border-slate-800 rounded-lg p-5">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-slate-800 rounded">
                    <Server className="w-5 h-5 text-slate-300" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-100">{asset.id}</h3>
                    <p className="text-xs text-slate-400">{asset.type}</p>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-mono font-bold ${
                  asset.currentRisk > 0.7 ? 'bg-red-500/20 text-red-400' :
                  asset.currentRisk > 0.4 ? 'bg-amber-500/20 text-amber-400' :
                  'bg-green-500/20 text-green-400'
                }`}>
                  RSK: {asset.currentRisk.toFixed(2)}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-slate-800">
                <div>
                  <div className="text-xs text-slate-500 mb-1">CRITICALITY</div>
                  <div className="font-mono text-slate-300">Tier {asset.criticality}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-1">RECENT INCIDENTS</div>
                  <div className="font-mono text-slate-300">{asset.incidents}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AssetIntelligence;
