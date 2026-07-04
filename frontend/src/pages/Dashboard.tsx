
import { Activity, ShieldAlert, Cpu, Network } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Dashboard() {
  const stats = [
    { label: 'Active Threats', value: '12', icon: ShieldAlert, color: 'text-red-500', bg: 'bg-red-500/10' },
    { label: 'Agents Online', value: '5/5', icon: Cpu, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { label: 'System Health', value: '98%', icon: Activity, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Network Events', value: '1.2k/s', icon: Network, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100">SOC Overview</h1>
        <p className="text-slate-400 text-sm mt-1">Autonomous Grid Security Status</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            key={stat.label} 
            className="glass-panel p-5 relative overflow-hidden group"
          >
            <div className="flex items-center gap-4 relative z-10">
              <div className={`p-3 rounded-xl ${stat.bg}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-400">{stat.label}</p>
                <h3 className="text-2xl font-bold text-slate-100 mt-1">{stat.value}</h3>
              </div>
            </div>
            {/* Subtle glow effect */}
            <div className={`absolute -right-6 -bottom-6 w-24 h-24 rounded-full blur-2xl opacity-20 group-hover:opacity-30 transition-opacity ${stat.bg.replace('/10', '')}`} />
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Activity Feed */}
        <div className="lg:col-span-2 glass-panel p-6 h-[400px]">
          <h3 className="text-lg font-medium text-slate-200 mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-400" />
            Agent Blackboard Activity
          </h3>
          <div className="flex items-center justify-center h-[300px] border border-dashed border-slate-700/50 rounded-lg">
            <p className="text-slate-500">Waiting for WebSocket data...</p>
          </div>
        </div>

        {/* Threat Map Placeholder */}
        <div className="glass-panel p-6 h-[400px]">
          <h3 className="text-lg font-medium text-slate-200 mb-4 flex items-center gap-2">
            <Network className="w-5 h-5 text-purple-400" />
            Grid Topology
          </h3>
          <div className="flex items-center justify-center h-[300px] border border-dashed border-slate-700/50 rounded-lg">
            <p className="text-slate-500">React Flow / Cytoscape Graph</p>
          </div>
        </div>
      </div>
    </div>
  )
}
