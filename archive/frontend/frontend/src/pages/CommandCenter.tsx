import React, { useEffect, useState } from 'react';
import { fetchIncidents, Incident } from '../services/api';
import { Link } from 'react-router-dom';
import { AlertTriangle, CheckCircle, ShieldAlert, Clock, Activity, ArrowRight } from 'lucide-react';

const CommandCenter: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchIncidents();
        setIncidents(data);
      } catch (err: any) {
        setError(err.message || "Failed to load incidents");
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) return <div className="p-8 text-slate-400 font-mono animate-pulse">LOADING SOC DATA...</div>;
  if (error) return <div className="p-8 text-red-400 font-mono flex items-center gap-2"><AlertTriangle/> SYSTEM ERROR: {error}</div>;

  const critical = incidents.filter(i => i.severity === 'CRITICAL' || i.risk_tier === 'CRITICAL');
  const actionRequired = incidents.filter(i => i.status === 'DETECTED' || i.approval_status === 'PENDING');

  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight">Command Center</h1>
        <p className="text-slate-400 text-sm mt-1">Real-time threat monitoring and incident response</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg flex flex-col">
          <div className="text-slate-400 text-xs font-semibold mb-2">ACTIVE INCIDENTS</div>
          <div className="text-3xl font-bold text-slate-100">{incidents.length}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg flex flex-col">
          <div className="text-red-400 text-xs font-semibold mb-2 flex items-center gap-1"><ShieldAlert className="w-4 h-4"/> CRITICAL RISK</div>
          <div className="text-3xl font-bold text-red-400">{critical.length}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg flex flex-col">
          <div className="text-amber-400 text-xs font-semibold mb-2 flex items-center gap-1"><Clock className="w-4 h-4"/> ACTION REQUIRED</div>
          <div className="text-3xl font-bold text-amber-400">{actionRequired.length}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg flex flex-col">
          <div className="text-blue-400 text-xs font-semibold mb-2 flex items-center gap-1"><Activity className="w-4 h-4"/> ASSETS AT RISK</div>
          <div className="text-3xl font-bold text-blue-400">{new Set(incidents.map(i => i.asset)).size}</div>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold mb-4 border-b border-slate-800 pb-2">Recent Events</h2>
        {incidents.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 p-8 text-center text-slate-500 rounded-lg">
            <CheckCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
            No active incidents detected.
          </div>
        ) : (
          <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950/50 text-slate-400 text-xs font-mono">
                <tr>
                  <th className="px-4 py-3 font-medium">INCIDENT ID</th>
                  <th className="px-4 py-3 font-medium">ASSET</th>
                  <th className="px-4 py-3 font-medium">SEVERITY</th>
                  <th className="px-4 py-3 font-medium">STATUS</th>
                  <th className="px-4 py-3 font-medium text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {incidents.map((incident) => (
                  <tr key={incident.incident_id} className="hover:bg-slate-800/20 transition-colors group">
                    <td className="px-4 py-3 font-mono text-slate-300">{incident.incident_id.substring(0, 8)}...</td>
                    <td className="px-4 py-3">{incident.asset}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        incident.severity === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 
                        'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {incident.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-300 text-xs font-mono">{incident.status}</td>
                    <td className="px-4 py-3 text-right">
                      <Link to={`/incidents/${incident.incident_id}`} className="text-blue-400 hover:text-blue-300 inline-flex items-center gap-1 text-xs font-semibold">
                        INVESTIGATE <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default CommandCenter;
