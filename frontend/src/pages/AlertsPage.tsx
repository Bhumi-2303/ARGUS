import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Filter,
  ShieldAlert,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  RotateCcw,
  CheckCircle2,
  Clock,
  ChevronRight,
  AlertOctagon
} from 'lucide-react';
import { Alert, Severity } from '../types';
import { getAlerts } from '../services/api';

type SortField = 'timestamp' | 'severity' | 'riskScore' | 'confidence';
type SortOrder = 'asc' | 'desc';

const SEVERITY_WEIGHT: Record<Severity, number> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1
};

const SEVERITY_BADGE_STYLE: Record<Severity, { bg: string; text: string; border: string; glow: string }> = {
  critical: {
    bg: 'bg-critical/15',
    text: 'text-critical',
    border: 'border-critical/40',
    glow: 'glow-critical'
  },
  high: {
    bg: 'bg-high/15',
    text: 'text-high',
    border: 'border-high/40',
    glow: 'glow-high'
  },
  medium: {
    bg: 'bg-warn/15',
    text: 'text-warn',
    border: 'border-warn/40',
    glow: 'glow-warn'
  },
  low: {
    bg: 'bg-info/15',
    text: 'text-info',
    border: 'border-info/40',
    glow: 'glow-info'
  }
};

const ALERT_STATUS_STYLE: Record<string, { bg: string; text: string; border: string }> = {
  active: { bg: 'bg-critical/10', text: 'text-critical', border: 'border-critical/30' },
  investigating: { bg: 'bg-warn/10', text: 'text-warn', border: 'border-warn/30' },
  contained: { bg: 'bg-info/10', text: 'text-info', border: 'border-info/30' },
  resolved: { bg: 'bg-safe/10', text: 'text-safe', border: 'border-safe/30' }
};

export const AlertsPage: React.FC = () => {
  const navigate = useNavigate();
  const [alertsList, setAlertsList] = useState<Alert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Filters State
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedAttackType, setSelectedAttackType] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('all');

  // Sorting State
  const [sortField, setSortField] = useState<SortField>('timestamp');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  useEffect(() => {
    let isMounted = true;
    async function loadAlerts() {
      try {
        const data = await getAlerts();
        if (isMounted) {
          setAlertsList(data);
          setLoading(false);
        }
      } catch (err) {
        console.error('Failed to fetch alerts:', err);
        if (isMounted) setLoading(false);
      }
    }
    loadAlerts();
    return () => {
      isMounted = false;
    };
  }, []);

  // Dynamically extract distinct attack types
  const availableAttackTypes = useMemo(() => {
    const types = new Set(alertsList.map((a) => a.attackType));
    return Array.from(types);
  }, [alertsList]);

  // Handle Sort Toggle
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  // Filter & Sort Logic
  const filteredAlerts = useMemo(() => {
    return alertsList
      .filter((alert) => {
        // Search Filter
        const q = searchQuery.toLowerCase();
        const matchesSearch =
          alert.id.toLowerCase().includes(q) ||
          alert.attackType.toLowerCase().includes(q) ||
          alert.source.toLowerCase().includes(q) ||
          (alert.target || '').toLowerCase().includes(q);

        // Severity Filter
        const matchesSeverity =
          selectedSeverity === 'all' || alert.severity === selectedSeverity;

        // Attack Type Filter
        const matchesAttack =
          selectedAttackType === 'all' || alert.attackType === selectedAttackType;

        // Status Filter
        const matchesStatus =
          selectedStatus === 'all' || alert.status === selectedStatus;

        // Time Range Filter (simulated)
        let matchesTime = true;
        if (selectedTimeRange === '1h') {
          const alertTime = new Date(alert.timestamp).getTime();
          const oneHourAgo = new Date('2026-08-27T14:34:00Z').getTime() - 60 * 60 * 1000;
          matchesTime = alertTime >= oneHourAgo;
        } else if (selectedTimeRange === '24h') {
          matchesTime = true; // All mock alerts are within 24h
        }

        return matchesSearch && matchesSeverity && matchesAttack && matchesStatus && matchesTime;
      })
      .sort((a, b) => {
        let compA = 0;
        let compB = 0;

        if (sortField === 'severity') {
          compA = SEVERITY_WEIGHT[a.severity];
          compB = SEVERITY_WEIGHT[b.severity];
        } else if (sortField === 'riskScore') {
          compA = a.riskScore;
          compB = b.riskScore;
        } else if (sortField === 'confidence') {
          compA = a.confidence || 0;
          compB = b.confidence || 0;
        } else if (sortField === 'timestamp') {
          compA = new Date(a.timestamp).getTime();
          compB = new Date(b.timestamp).getTime();
        }

        return sortOrder === 'asc' ? compA - compB : compB - compA;
      });
  }, [
    alertsList,
    searchQuery,
    selectedSeverity,
    selectedAttackType,
    selectedStatus,
    selectedTimeRange,
    sortField,
    sortOrder
  ]);

  // Reset Filters
  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedSeverity('all');
    setSelectedAttackType('all');
    setSelectedStatus('all');
    setSelectedTimeRange('all');
    setSortField('timestamp');
    setSortOrder('desc');
  };

  const isFilterActive =
    searchQuery !== '' ||
    selectedSeverity !== 'all' ||
    selectedAttackType !== 'all' ||
    selectedStatus !== 'all' ||
    selectedTimeRange !== 'all';

  // KPI Metrics
  const totalAlerts = alertsList.length;
  const criticalCount = alertsList.filter((a) => a.severity === 'critical').length;
  const activeCount = alertsList.filter((a) => a.status === 'active').length;
  const avgRisk = totalAlerts > 0 ? Math.round(alertsList.reduce((acc, a) => acc + a.riskScore, 0) / totalAlerts) : 0;

  return (
    <div className="space-y-6">
      {/* Top Header & Summary KPIs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Alert Triage & Incidents</h1>
          <p className="text-xs font-mono text-text-secondary mt-1">
            REAL-TIME THREAT INGESTION & AUTOMATED SEVERITY PRIORITIZATION QUEUE
          </p>
        </div>
      </div>

      {/* KPI Cards Banner */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-4 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-info/10 border border-info/20 text-info">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-text-secondary uppercase tracking-wider block">TOTAL ALERTS</span>
            <span className="text-xl font-bold font-mono text-text-primary mt-0.5 block">{totalAlerts}</span>
          </div>
        </div>

        <div className="glass-panel p-4 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-critical/15 border border-critical/30 text-critical glow-critical">
            <AlertOctagon className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-text-secondary uppercase tracking-wider block">CRITICAL THREATS</span>
            <span className="text-xl font-bold font-mono text-critical mt-0.5 block">{criticalCount}</span>
          </div>
        </div>

        <div className="glass-panel p-4 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-warn/10 border border-warn/20 text-warn">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-text-secondary uppercase tracking-wider block">ACTIVE QUEUE</span>
            <span className="text-xl font-bold font-mono text-warn mt-0.5 block">{activeCount}</span>
          </div>
        </div>

        <div className="glass-panel p-4 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-bg-surface-raised border border-border-muted text-info">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-mono text-text-secondary uppercase tracking-wider block">AVG RISK SCORE</span>
            <span className="text-xl font-bold font-mono text-text-primary mt-0.5 block">{avgRisk}/100</span>
          </div>
        </div>
      </div>

      {/* Toolbar & Filters */}
      <div className="glass-panel p-4 space-y-3">
        <div className="flex flex-col lg:flex-row gap-3 items-stretch lg:items-center justify-between">
          {/* Search Input */}
          <div className="relative flex-1 min-w-[260px]">
            <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search alert ID, attack type, source IP or target node..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-lg bg-bg-surface border border-border-muted text-xs text-text-primary placeholder:text-text-secondary focus:outline-none focus:border-info"
            />
          </div>

          {/* Filter Select Controls */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Severity Filter */}
            <div className="flex items-center gap-1.5 bg-bg-surface px-2.5 py-1.5 rounded-lg border border-border-muted text-xs">
              <Filter className="w-3.5 h-3.5 text-text-secondary" />
              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="bg-transparent text-text-primary focus:outline-none font-mono text-xs cursor-pointer"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            {/* Attack Type Filter */}
            <div className="flex items-center gap-1.5 bg-bg-surface px-2.5 py-1.5 rounded-lg border border-border-muted text-xs">
              <select
                value={selectedAttackType}
                onChange={(e) => setSelectedAttackType(e.target.value)}
                className="bg-transparent text-text-primary focus:outline-none font-mono text-xs cursor-pointer max-w-[150px]"
              >
                <option value="all">All Attack Types</option>
                {availableAttackTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-1.5 bg-bg-surface px-2.5 py-1.5 rounded-lg border border-border-muted text-xs">
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="bg-transparent text-text-primary focus:outline-none font-mono text-xs cursor-pointer"
              >
                <option value="all">All Statuses</option>
                <option value="active">Active</option>
                <option value="investigating">Investigating</option>
                <option value="contained">Contained</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>

            {/* Time Range Filter */}
            <div className="flex items-center gap-1.5 bg-bg-surface px-2.5 py-1.5 rounded-lg border border-border-muted text-xs">
              <Clock className="w-3.5 h-3.5 text-text-secondary" />
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="bg-transparent text-text-primary focus:outline-none font-mono text-xs cursor-pointer"
              >
                <option value="all">All Time</option>
                <option value="1h">Last 1 Hour</option>
                <option value="24h">Last 24 Hours</option>
              </select>
            </div>

            {/* Reset Filters Button */}
            {isFilterActive && (
              <button
                onClick={handleResetFilters}
                className="px-2.5 py-1.5 rounded-lg bg-bg-surface border border-border-muted text-text-secondary hover:text-text-primary text-xs font-mono flex items-center gap-1.5 transition-colors"
                title="Reset all filters"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Alerts Table */}
      <div className="glass-panel overflow-hidden border border-border-muted rounded-xl">
        {loading ? (
          <div className="p-12 text-center text-text-secondary font-mono text-xs flex flex-col items-center justify-center gap-3">
            <div className="w-6 h-6 border-2 border-info border-t-transparent rounded-full animate-spin" />
            <span>Loading alert telemetry queue...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-text-primary select-none">
              <thead className="bg-bg-surface-raised border-b border-border-muted font-mono text-[11px] text-text-secondary uppercase">
                <tr>
                  <th
                    className="p-3.5 cursor-pointer hover:text-text-primary transition-colors"
                    onClick={() => handleSort('severity')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Severity</span>
                      {sortField === 'severity' ? (
                        sortOrder === 'asc' ? <ArrowUp className="w-3 h-3 text-info" /> : <ArrowDown className="w-3 h-3 text-info" />
                      ) : (
                        <ArrowUpDown className="w-3 h-3 text-text-secondary/40" />
                      )}
                    </div>
                  </th>
                  <th className="p-3.5">Attack Type & ID</th>
                  <th className="p-3.5">Source → Target Flow</th>
                  <th
                    className="p-3.5 cursor-pointer hover:text-text-primary transition-colors"
                    onClick={() => handleSort('confidence')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Confidence</span>
                      {sortField === 'confidence' ? (
                        sortOrder === 'asc' ? <ArrowUp className="w-3 h-3 text-info" /> : <ArrowDown className="w-3 h-3 text-info" />
                      ) : (
                        <ArrowUpDown className="w-3 h-3 text-text-secondary/40" />
                      )}
                    </div>
                  </th>
                  <th
                    className="p-3.5 cursor-pointer hover:text-text-primary transition-colors"
                    onClick={() => handleSort('riskScore')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Risk Score</span>
                      {sortField === 'riskScore' ? (
                        sortOrder === 'asc' ? <ArrowUp className="w-3 h-3 text-info" /> : <ArrowDown className="w-3 h-3 text-info" />
                      ) : (
                        <ArrowUpDown className="w-3 h-3 text-text-secondary/40" />
                      )}
                    </div>
                  </th>
                  <th
                    className="p-3.5 cursor-pointer hover:text-text-primary transition-colors"
                    onClick={() => handleSort('timestamp')}
                  >
                    <div className="flex items-center gap-1">
                      <span>Timestamp</span>
                      {sortField === 'timestamp' ? (
                        sortOrder === 'asc' ? <ArrowUp className="w-3 h-3 text-info" /> : <ArrowDown className="w-3 h-3 text-info" />
                      ) : (
                        <ArrowUpDown className="w-3 h-3 text-text-secondary/40" />
                      )}
                    </div>
                  </th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-muted/50">
                {filteredAlerts.map((alert) => {
                  const sevStyle = SEVERITY_BADGE_STYLE[alert.severity] || SEVERITY_BADGE_STYLE.medium;
                  const statStyle = ALERT_STATUS_STYLE[alert.status] || ALERT_STATUS_STYLE.active;

                  return (
                    <tr
                      key={alert.id}
                      onClick={() => navigate(`/alerts/${alert.id}`)}
                      className="cursor-pointer transition-colors hover:bg-bg-surface-raised/80 group"
                    >
                      {/* Severity Pill */}
                      <td className="p-3.5">
                        <span
                          className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider border ${sevStyle.bg} ${sevStyle.text} ${sevStyle.border} ${sevStyle.glow}`}
                        >
                          {alert.severity}
                        </span>
                      </td>

                      {/* Attack Type & ID */}
                      <td className="p-3.5">
                        <div className="font-semibold text-text-primary group-hover:text-info transition-colors">
                          {alert.attackType}
                        </div>
                        <div className="font-mono text-[10px] text-text-secondary mt-0.5">
                          {alert.id}
                        </div>
                      </td>

                      {/* Source -> Target */}
                      <td className="p-3.5 font-mono text-[11px]">
                        <div className="text-text-primary truncate max-w-[240px]" title={alert.source}>
                          {alert.source}
                        </div>
                        <div className="text-text-secondary flex items-center gap-1 mt-0.5 truncate max-w-[240px]" title={alert.target || 'Not provided'}>
                          <span>→</span> {alert.target || 'Not provided'}
                        </div>
                      </td>

                      {/* Confidence */}
                      <td className="p-3.5 font-mono font-bold">
                        <div className="flex items-center gap-2">
                          <span className="text-text-primary">{alert.confidence !== undefined ? `${(alert.confidence * 100).toFixed(0)}%` : 'N/A'}</span>
                          <div className="w-12 h-1.5 rounded-full bg-bg-surface-raised overflow-hidden">
                            <div
                              className="h-full bg-info"
                              style={{ width: `${(alert.confidence || 0) * 100}%` }}
                            />
                          </div>
                        </div>
                      </td>

                      {/* Risk Score */}
                      <td className="p-3.5 font-mono font-bold text-sm">
                        <span
                          className={
                            alert.riskScore > 75
                              ? 'text-critical'
                              : alert.riskScore > 50
                              ? 'text-warn'
                              : 'text-safe'
                          }
                        >
                          {alert.riskScore}/100
                        </span>
                      </td>

                      {/* Timestamp */}
                      <td className="p-3.5 font-mono text-[11px] text-text-secondary whitespace-nowrap">
                        {new Date(alert.timestamp).toLocaleTimeString()} UTC
                      </td>

                      {/* Status */}
                      <td className="p-3.5">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold uppercase border ${statStyle.bg} ${statStyle.text} ${statStyle.border}`}
                        >
                          <span
                            className="w-1.5 h-1.5 rounded-full"
                            style={{
                              backgroundColor:
                                alert.status === 'active'
                                  ? '#ef4444'
                                  : alert.status === 'investigating'
                                  ? '#eab308'
                                  : alert.status === 'contained'
                                  ? '#22d3ee'
                                  : '#22c55e'
                            }}
                          />
                          {alert.status}
                        </span>
                      </td>

                      {/* Action Chevron */}
                      <td className="p-3.5 text-right">
                        <ChevronRight className="w-4 h-4 text-text-secondary group-hover:text-info group-hover:translate-x-1 transition-all inline-block" />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {/* Empty State */}
            {filteredAlerts.length === 0 && (
              <div className="p-12 text-center text-text-secondary space-y-3">
                <ShieldAlert className="w-8 h-8 text-text-secondary/40 mx-auto" />
                <p className="font-mono text-xs">No alerts match the selected filter criteria.</p>
                <button
                  onClick={handleResetFilters}
                  className="px-3 py-1.5 rounded-lg bg-info/10 border border-info/30 text-info text-xs font-mono hover:bg-info/20 transition-colors inline-flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Reset All Filters</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertsPage;
