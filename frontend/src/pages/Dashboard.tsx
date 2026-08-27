import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, AlertTriangle, Network, Cpu, Activity, Gauge, Brain, FileText, ArrowRight, ServerCrash, Eye } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area, XAxis, YAxis, Tooltip, RadialBarChart, RadialBar, Legend, ReferenceDot } from 'recharts';

import { mockAlerts, mockAttackCategories, mockModelPerformance, mockAttackTrend, mockAuditEvents } from '../services/api';
import Topology3D from '../components/network/Topology3D';

export default function Dashboard() {
  const [tickerIndex, setTickerIndex] = useState(0);

  // Ticker animation
  useEffect(() => {
    const timer = setInterval(() => {
      setTickerIndex((prev) => (prev + 1) % mockAuditEvents.length);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  // 1. KPI Data
  const kpis = [
    { label: 'Active Threats', value: '12', delta: '+2 since last hour', icon: ShieldAlert, color: 'text-red-500', border: 'border-l-red-500' },
    { label: 'Critical Alerts', value: '4', delta: '+1 since last hour', icon: AlertTriangle, color: 'text-orange-500', border: 'border-l-orange-500' },
    { label: 'At-Risk Nodes', value: '7', delta: 'No change', icon: ServerCrash, color: 'text-yellow-500', border: 'border-l-yellow-500' },
    { label: 'Agents Online', value: '5/5', delta: 'All systems go', icon: Cpu, color: 'text-emerald-500', border: 'border-l-emerald-500' },
    { label: 'System Health', value: '98%', delta: '+1% since yesterday', icon: Activity, color: 'text-blue-500', border: 'border-l-blue-500' },
    { label: 'Global Risk Score', value: '82', delta: '+5 points', icon: Gauge, color: 'text-purple-500', border: 'border-l-purple-500', isGauge: true },
  ];

  // Pipeline Agents
  const pipeline = [
    { id: 'ag-detect', name: 'DETECT', icon: Eye, active: true },
    { id: 'ag-assess', name: 'ASSESS', icon: Activity, active: true },
    { id: 'ag-explain', name: 'EXPLAIN', icon: Brain, active: true },
    { id: 'ag-respond', name: 'RESPOND', icon: ShieldAlert, active: true },
    { id: 'ag-report', name: 'REPORT', icon: FileText, active: true },
  ];

  const severityColors: Record<string, string> = {
    critical: 'bg-red-500 text-white',
    high: 'bg-orange-500 text-white',
    medium: 'bg-yellow-500 text-white',
    low: 'bg-blue-500 text-white',
  };

  return (
    <div className="flex flex-col gap-6 h-full pb-10 relative">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">Command Center</h1>
          <p className="text-slate-400 text-sm mt-1">ARGUS Grid Security Overview</p>
        </div>
      </div>

      {/* 1. KPI Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {kpis.map((kpi, i) => (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            key={kpi.label}
            className={`glass-panel p-4 border-l-4 ${kpi.border} flex flex-col justify-between`}
          >
            <div className="flex justify-between items-start mb-2">
              <span className="text-sm font-medium text-slate-400">{kpi.label}</span>
              <kpi.icon className={`w-5 h-5 ${kpi.color}`} />
            </div>
            <div className="flex items-end gap-2">
              {kpi.isGauge ? (
                <div className="flex items-center gap-2">
                   <span className="text-3xl font-bold text-slate-100">{kpi.value}</span>
                   <span className="text-sm text-slate-500">/100</span>
                </div>
              ) : (
                <span className="text-3xl font-bold text-slate-100">{kpi.value}</span>
              )}
            </div>
            <span className="text-xs text-slate-500 mt-2 block">{kpi.delta}</span>
          </motion.div>
        ))}
      </div>

      {/* 2. Main Area (Topology + Live Alerts/Donut) */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 flex-1 min-h-[400px]">
        {/* Left: Topology */}
        <div className="xl:col-span-2 glass-panel p-4 flex flex-col">
          <h2 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <Network className="w-5 h-5 text-blue-400" />
            Smart Grid Network Topology
          </h2>
          <div className="flex-1 rounded-lg overflow-hidden relative">
            <Topology3D />
          </div>
        </div>

        {/* Right: Alerts & Donut */}
        <div className="flex flex-col gap-6">
          {/* Live Alerts */}
          <div className="glass-panel p-4 flex-1 flex flex-col min-h-[250px]">
            <h2 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-red-400" />
              Live Alerts
            </h2>
            <div className="flex flex-col gap-3 flex-1 overflow-y-auto pr-2">
              {mockAlerts.map((alert) => (
                <Link to={`/alerts/${alert.id}`} key={alert.id}>
                  <div className="bg-slate-900/50 hover:bg-slate-800/80 transition-colors border border-slate-700/50 rounded-lg p-3 flex flex-col gap-2">
                    <div className="flex justify-between items-center">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${severityColors[alert.severity]}`}>
                        {alert.severity}
                      </span>
                      <span className="text-xs text-slate-400">{alert.timestamp}</span>
                    </div>
                    <div className="text-sm font-medium text-slate-200 truncate">{alert.name}</div>
                    <div className="flex justify-between items-center text-xs text-slate-400">
                      <div className="flex items-center gap-1 truncate">
                        <span>{alert.source}</span>
                        <ArrowRight className="w-3 h-3" />
                        <span>{alert.target}</span>
                      </div>
                      <span className="text-emerald-400 font-mono">{alert.confidence}%</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Top Attack Categories */}
          <div className="glass-panel p-4 h-[250px] flex flex-col shrink-0">
            <h2 className="text-sm font-semibold text-slate-200 mb-2">Top Attack Categories</h2>
            <div className="flex-1 w-full h-full min-h-[150px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={mockAttackCategories}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={2}
                    dataKey="count"
                    stroke="none"
                  >
                    {mockAttackCategories.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }}
                    itemStyle={{ color: '#f8fafc' }}
                  />
                  <Legend verticalAlign="middle" align="right" layout="vertical" wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[220px]">
        {/* Model Ensemble */}
        <div className="glass-panel p-4 flex flex-col">
          <h2 className="text-sm font-semibold text-slate-200 mb-2">AI Model Ensemble Performance</h2>
          <div className="flex-1 flex items-center justify-around mt-4">
            {mockModelPerformance.map((model) => (
              <div key={model.name} className="flex flex-col items-center">
                <div className="w-20 h-20 relative">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadialBarChart 
                      cx="50%" cy="50%" 
                      innerRadius="70%" outerRadius="100%" 
                      barSize={8} 
                      data={[{ name: model.name, value: model.confidence, fill: model.color }]}
                      startAngle={90} endAngle={-270}
                    >
                      <RadialBar
                        background={{ fill: '#334155' }}
                        dataKey="value"
                        cornerRadius={5}
                      />
                    </RadialBarChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-lg font-bold text-slate-200">{model.confidence}%</span>
                  </div>
                </div>
                <span className="text-[10px] font-medium text-slate-400 mt-3 text-center uppercase tracking-wider">{model.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Attack Trend */}
        <div className="glass-panel p-4 flex flex-col">
          <h2 className="text-sm font-semibold text-slate-200 mb-2">Attack Trend (24h)</h2>
          <div className="flex-1 w-full mt-2 min-h-[120px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockAttackTrend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="volume" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorVolume)" />
                {/* Highlight peak */}
                {mockAttackTrend.filter(d => d.isPeak).map((d, i) => (
                  <ReferenceDot key={i} x={d.time} y={d.volume} r={4} fill="#ef4444" stroke="#fff" strokeWidth={2} />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Multi-Agent Orchestration */}
        <div className="glass-panel p-4 flex flex-col">
          <h2 className="text-sm font-semibold text-slate-200 mb-4">Multi-Agent Orchestration</h2>
          <div className="flex-1 flex items-center justify-between relative px-4 mt-2">
            {/* Connecting Line */}
            <div className="absolute top-1/2 left-8 right-8 h-0.5 bg-slate-700 -translate-y-1/2 z-0" />
            
            {pipeline.map((agent) => (
              <React.Fragment key={agent.id}>
                <Link to={`/pipeline/${agent.id}`} className="z-10 group relative flex flex-col items-center outline-none">
                  <div className="bg-slate-900 border border-slate-700 group-hover:border-blue-500 group-hover:bg-slate-800 transition-all rounded-full w-12 h-12 flex items-center justify-center shadow-lg shadow-black/50 relative">
                    <agent.icon className="w-5 h-5 text-blue-400 group-hover:text-blue-300" />
                    {/* Active Dot */}
                    {agent.active && (
                      <span className="absolute top-0 right-0 w-3 h-3 bg-emerald-500 border-2 border-slate-900 rounded-full"></span>
                    )}
                  </div>
                  <div className="absolute -bottom-7 left-1/2 -translate-x-1/2 text-[9px] font-bold text-slate-400 group-hover:text-slate-200 uppercase tracking-wider whitespace-nowrap">
                    {agent.name}
                  </div>
                </Link>
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* 4. Bottom Bar Ticker */}
      <div className="fixed bottom-0 left-0 lg:left-64 right-0 h-10 bg-slate-900/90 backdrop-blur border-t border-slate-800 flex items-center px-4 z-50">
        <div className="flex items-center gap-2 mr-4 shrink-0">
          <Activity className="w-4 h-4 text-emerald-500 animate-pulse" />
          <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Live Audit</span>
        </div>
        
        <div className="flex-1 overflow-hidden h-full flex items-center relative">
          <AnimatePresence mode="wait">
            {mockAuditEvents.length > 0 && (
              <motion.div
                key={tickerIndex}
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: -20, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="absolute flex items-center gap-3 text-sm text-slate-400 whitespace-nowrap"
              >
                <span className="font-mono text-xs text-slate-500">{mockAuditEvents[tickerIndex].timestamp}</span>
                <div className={`w-2 h-2 rounded-full ${
                  mockAuditEvents[tickerIndex].type === 'error' ? 'bg-red-500' :
                  mockAuditEvents[tickerIndex].type === 'warning' ? 'bg-yellow-500' :
                  mockAuditEvents[tickerIndex].type === 'success' ? 'bg-emerald-500' : 'bg-blue-500'
                }`} />
                <span className="truncate">{mockAuditEvents[tickerIndex].message}</span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <Link to="/reports" className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 ml-4 transition-colors shrink-0">
          View Full Log <ArrowRight className="w-3 h-3" />
        </Link>
      </div>

    </div>
  );
}
