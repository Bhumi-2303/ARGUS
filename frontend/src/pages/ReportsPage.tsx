import React, { useState, useEffect, useMemo } from 'react';
import {
  ShieldCheck,
  Activity,
  Clock,
  Download,
  Search,
  FileCheck,
  Sparkles,
  Cpu
} from 'lucide-react';

import { AuditEvent, AgentId } from '../types';
import { getAuditEvents, getAlerts, getExplanations } from '../services/api';

const AGENT_DOT_COLORS: Record<AgentId | 'system', { color: string; bg: string; border: string; glow: string }> = {
  detection: { color: '#22d3ee', bg: 'bg-info/10', border: 'border-info/30', glow: 'glow-info' },
  risk: { color: '#eab308', bg: 'bg-warn/10', border: 'border-warn/30', glow: 'glow-warn' },
  explainability: { color: '#a855f7', bg: 'bg-xai/10', border: 'border-xai/30', glow: 'glow-xai' },
  response: { color: '#ef4444', bg: 'bg-critical/10', border: 'border-critical/30', glow: 'glow-critical' },
  reporting: { color: '#22c55e', bg: 'bg-safe/10', border: 'border-safe/30', glow: 'glow-safe' },
  system: { color: '#3b82f6', bg: 'bg-blue-500/10', border: 'border-blue-500/30', glow: '' }
};

interface ReportEntry {
  id: string;
  title: string;
  category: string;
  date: string;
  fileSize: string;
  status: 'Ready' | 'Generating';
}

const mockReportsList: ReportEntry[] = [
  {
    id: 'REP-2026-0391',
    title: 'NERC-CIP Substation Compliance Audit Report (Q3 2026)',
    category: 'Regulatory Compliance',
    date: '2026-08-27T14:00:00Z',
    fileSize: '4.2 MB',
    status: 'Ready'
  },
  {
    id: 'REP-2026-0392',
    title: '24-Hour SCADA Telemetry Anomaly & Incident Summary',
    category: 'Operational Security',
    date: '2026-08-27T12:30:00Z',
    fileSize: '2.8 MB',
    status: 'Ready'
  },
  {
    id: 'REP-2026-0393',
    title: 'ASDU Command Spooling Incident Post-Mortem Analysis',
    category: 'Incident Post-Mortem',
    date: '2026-08-27T10:15:00Z',
    fileSize: '6.1 MB',
    status: 'Ready'
  },
  {
    id: 'REP-2026-0394',
    title: 'SHAP Feature Attribution & Model Explainability Audit',
    category: 'AI/XAI Model Governance',
    date: '2026-08-26T18:00:00Z',
    fileSize: '3.5 MB',
    status: 'Ready'
  }
];

export const ReportsPage: React.FC = () => {
  const [eventsList, setEventsList] = useState<AuditEvent[]>([]);
  const [totalAlertsCount, setTotalAlertsCount] = useState<number>(0);
  const [explanationsCount, setExplanationsCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  // Audit Filters
  const [selectedAgent, setSelectedAgent] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');

  useEffect(() => {
    let mounted = true;
    async function loadAuditData() {
      try {
        const [events, alerts, exps] = await Promise.all([
          getAuditEvents(),
          getAlerts(),
          getExplanations()
        ]);
        if (mounted) {
          setEventsList(events);
          setTotalAlertsCount(alerts.length);
          setExplanationsCount(exps.length);
          setLoading(false);
        }
      } catch (err) {
        console.error('Failed to load audit data:', err);
        if (mounted) setLoading(false);
      }
    }
    loadAuditData();

    return () => {
      mounted = false;
    };
  }, []);

  const filteredEvents = useMemo(() => {
    return eventsList.filter((evt) => {
      const matchesAgent = selectedAgent === 'all' || evt.agent === selectedAgent;
      const matchesSearch =
        evt.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        evt.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        evt.agent.toLowerCase().includes(searchTerm.toLowerCase());

      return matchesAgent && matchesSearch;
    });
  }, [eventsList, selectedAgent, searchTerm]);

  return (
    <div className="space-y-6 select-none">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Compliance & Incident Reports</h1>
          <p className="text-xs font-mono text-text-secondary mt-1">
            IMMUTABLE AUDIT TRAIL LOGGING & NERC-CIP REGULATORY COMPLIANCE EXPORTS
          </p>
        </div>
      </div>

      {/* Summary KPI Strip */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-4 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-info/10 border border-info/20 text-info">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-text-secondary uppercase tracking-wider block">SECURITY EVENTS</span>
            <span className="text-xl font-bold font-mono text-text-primary mt-0.5 block">1,248</span>
          </div>
        </div>

        <div className="glass-panel p-4 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-xai/10 border border-xai/20 text-xai glow-xai">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-text-secondary uppercase tracking-wider block">EXPLAINED ALERTS</span>
            <span className="text-xl font-bold font-mono text-text-primary mt-0.5 block">
              {explanationsCount}/{totalAlertsCount} ({((explanationsCount / Math.max(1, totalAlertsCount)) * 100).toFixed(0)}%)
            </span>
          </div>
        </div>

        <div className="glass-panel p-4 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-warn/10 border border-warn/20 text-warn">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-text-secondary uppercase tracking-wider block">AGENT ACTIONS</span>
            <span className="text-xl font-bold font-mono text-warn mt-0.5 block">48</span>
          </div>
        </div>

        <div className="glass-panel p-4 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-safe/10 border border-safe/30 text-safe glow-safe">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-text-secondary uppercase tracking-wider block">AUDIT COMPLETENESS</span>
            <span className="text-xl font-bold font-mono text-safe mt-0.5 block">99.4%</span>
          </div>
        </div>
      </div>

      {/* Main 2-Column Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 Cols): Chronological Audit Trail */}
        <div className="lg:col-span-2 space-y-4">
          <div className="glass-panel p-6 space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-border-muted pb-3">
              <h3 className="text-sm font-mono font-bold tracking-wider text-text-secondary uppercase flex items-center gap-2">
                <Clock className="w-4 h-4 text-info" /> CHRONOLOGICAL SYSTEM AUDIT TRAIL
              </h3>

              {/* Filters */}
              <div className="flex flex-wrap items-center gap-2">
                {/* Search */}
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-text-secondary absolute left-2.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Search logs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8 pr-3 py-1 rounded bg-bg-surface border border-border-muted text-[11px] font-mono text-text-primary placeholder:text-text-secondary focus:outline-none focus:border-info w-36"
                  />
                </div>

                {/* Agent Filter Options */}
                <div className="flex items-center gap-1">
                  <select
                    value={selectedAgent}
                    onChange={(e) => setSelectedAgent(e.target.value)}
                    className="px-2.5 py-1 rounded bg-bg-surface border border-border-muted text-[11px] font-mono text-text-primary focus:outline-none focus:border-info cursor-pointer"
                  >
                    <option value="all">All Agents ({eventsList.length})</option>
                    <option value="detection">Detection</option>
                    <option value="risk">Risk</option>
                    <option value="explainability">Explainability</option>
                    <option value="response">Response</option>
                    <option value="reporting">Reporting</option>
                    <option value="system">System</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Audit Stream List */}
            {loading ? (
              <div className="p-8 text-center text-text-secondary font-mono text-xs">
                Loading audit stream...
              </div>
            ) : (
              <div className="space-y-2.5">
                {filteredEvents.map((evt) => {
                  const style = AGENT_DOT_COLORS[evt.agent] || AGENT_DOT_COLORS.system;

                  return (
                    <div
                      key={evt.id}
                      className="p-3.5 rounded-lg bg-bg-surface border border-border-muted/70 flex items-start gap-3 transition-colors hover:bg-bg-surface-raised/60"
                    >
                      {/* Colored Agent Status Indicator Dot */}
                      <div className="flex items-center gap-2 mt-0.5">
                        <span
                          className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${style.glow}`}
                          style={{ backgroundColor: style.color }}
                        />
                      </div>

                      {/* Event Details */}
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center justify-between">
                          <span
                            className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${style.bg} ${style.border}`}
                            style={{ color: style.color }}
                          >
                            {evt.agent}
                          </span>
                          <span className="text-[10px] font-mono text-text-secondary">
                            {new Date(evt.timestamp).toLocaleTimeString()} UTC
                          </span>
                        </div>

                        <p className="text-xs text-text-primary font-mono leading-relaxed">
                          {evt.message}
                        </p>
                      </div>
                    </div>
                  );
                })}

                {filteredEvents.length === 0 && (
                  <div className="p-8 text-center text-text-secondary font-mono text-xs">
                    No audit log entries match the selected filter.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column (1 Col): Recent Reports List */}
        <div className="space-y-4">
          <div className="glass-panel p-6 space-y-4">
            <h3 className="text-sm font-mono font-bold tracking-wider text-text-secondary uppercase flex items-center gap-2 border-b border-border-muted pb-3">
              <FileCheck className="w-4 h-4 text-info" /> RECENT COMPLIANCE REPORTS
            </h3>

            <div className="space-y-3 font-mono text-xs">
              {mockReportsList.map((report) => (
                <div key={report.id} className="p-4 rounded-lg bg-bg-surface border border-border-muted space-y-3">
                  <div>
                    <span className="text-[10px] text-info font-bold uppercase tracking-wider block">
                      {report.category}
                    </span>
                    <h4 className="text-sm font-bold text-text-primary mt-0.5 font-sans leading-tight">
                      {report.title}
                    </h4>
                  </div>

                  <div className="flex justify-between items-center text-[10px] text-text-secondary border-t border-border-muted/50 pt-2">
                    <span>{new Date(report.date).toLocaleDateString()}</span>
                    <span>{report.fileSize}</span>
                  </div>

                  {/* Disabled Export PDF Button */}
                  <div>
                    <button
                      disabled
                      className="w-full px-3 py-2 rounded-lg bg-bg-surface-raised border border-border-muted text-text-secondary/50 text-xs font-mono font-medium flex items-center justify-center gap-2 cursor-not-allowed opacity-60"
                      title="Not yet wired to backend API"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Export PDF</span>
                      <span className="text-[9px] text-text-secondary/40 font-mono">(Backend Unwired)</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;
