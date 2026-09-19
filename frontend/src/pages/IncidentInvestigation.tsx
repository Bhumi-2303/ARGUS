import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchIncident, fetchIncidentTimeline, updateIncidentStatus, approveIncident, Incident } from '../services/api';
import { ArrowLeft, ShieldAlert, Cpu, Network, CheckCircle, XCircle } from 'lucide-react';
import AgentTrace from '../components/AgentTrace';

const IncidentInvestigation: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<Incident | null>(null);
  // timeline state removed
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approving, setApproving] = useState(false);

  useEffect(() => {
    if (!id) return;
    const loadData = async () => {
      try {
        setLoading(true);
        const [incData] = await Promise.all([
          fetchIncident(id),
          fetchIncidentTimeline(id).catch(() => [])
        ]);
        setIncident(incData);
        // setTimeline(tlData);
      } catch (err: any) {
        setError(err.message || "Failed to load incident details");
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [id]);

  const handleApprove = async () => {
    if (!incident) return;
    try {
      setApproving(true);
      const updated = await approveIncident(incident.incident_id, "Approved by SOC operator");
      setIncident(updated);
    } catch (err: any) {
      alert("Failed to approve: " + err.message);
    } finally {
      setApproving(false);
    }
  };

  const handleReject = async () => {
    if (!incident) return;
    try {
      setApproving(true);
      const updated = await updateIncidentStatus(incident.incident_id, "RESOLVED", "SOC Operator");
      setIncident(updated);
    } catch (err: any) {
      alert("Failed to reject: " + err.message);
    } finally {
      setApproving(false);
    }
  };

  if (loading) return <div className="p-8 text-slate-400 font-mono animate-pulse">RETRIEVING INCIDENT...</div>;
  if (error || !incident) return <div className="p-8 text-red-400 font-mono">ERROR: {error || "Not found"}</div>;

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-12">
      <div className="flex items-center gap-4 border-b border-slate-800 pb-4">
        <Link to="/" className="p-2 rounded hover:bg-slate-800 text-slate-400 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold tracking-tight">Incident {incident.incident_id.substring(0, 8)}</h1>
            <span className={`px-2 py-0.5 rounded text-xs font-bold border ${
                incident.severity === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
                'bg-amber-500/10 text-amber-400 border-amber-500/20'
            }`}>{incident.severity}</span>
            <span className="px-2 py-0.5 rounded text-xs font-mono border bg-slate-800 text-slate-300 border-slate-700">
              {incident.status}
            </span>
          </div>
          <p className="text-slate-400 text-sm font-mono mt-1">Asset: {incident.asset}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-slate-400" />
              Threat Context
            </h3>
            <div className="prose prose-invert prose-sm max-w-none text-slate-400 space-y-4">
              <div>
                <strong className="text-slate-200">Detector Output:</strong>
                <p className="mt-1">{incident.detector_summary || 'No detector summary available.'}</p>
              </div>
              <div>
                <strong className="text-slate-200">Knowledge Context:</strong>
                <p className="mt-1">{incident.knowledge_summary || 'No knowledge context available.'}</p>
              </div>
            </div>
          </div>

          <AgentTrace incident={incident} />
        </div>

        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
              <Network className="w-4 h-4 text-slate-400" />
              Risk Assessment
            </h3>
            <div className="space-y-4 text-sm">
              <div className="flex justify-between items-center border-b border-slate-800/50 pb-2">
                <span className="text-slate-400">Risk Score</span>
                <span className="font-mono text-slate-200">{incident.risk_score?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-800/50 pb-2">
                <span className="text-slate-400">Risk Tier</span>
                <span className="font-mono text-slate-200">{incident.risk_tier || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center pb-2">
                <span className="text-slate-400">Criticality</span>
                <span className="font-mono text-slate-200">{incident.asset_criticality || 'N/A'}</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-slate-400" />
              Response Policy
            </h3>
            
            <div className="space-y-4">
              <div className="p-3 bg-slate-950 rounded border border-slate-800 text-sm text-slate-300">
                {incident.response?.description || incident.decision?.action || 'No response recommended.'}
              </div>

              {incident.approval_status === 'PENDING' && (
                <div className="flex gap-3 mt-4">
                  <button 
                    onClick={handleApprove} 
                    disabled={approving}
                    className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-medium py-2 px-4 rounded transition-colors flex items-center justify-center gap-2 text-sm disabled:opacity-50"
                  >
                    <CheckCircle className="w-4 h-4" /> Approve
                  </button>
                  <button 
                    onClick={handleReject} 
                    disabled={approving}
                    className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium py-2 px-4 rounded transition-colors flex items-center justify-center gap-2 text-sm disabled:opacity-50 border border-slate-700"
                  >
                    <XCircle className="w-4 h-4" /> Reject
                  </button>
                </div>
              )}
              {incident.approval_status === 'APPROVED' && (
                <div className="p-3 bg-green-500/10 border border-green-500/20 text-green-400 text-sm rounded flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Action Approved
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IncidentInvestigation;
