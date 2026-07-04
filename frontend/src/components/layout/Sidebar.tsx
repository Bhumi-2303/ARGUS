
import { Link, useLocation } from 'react-router-dom'
import { Shield, Activity, Network, Cpu, Settings, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { icon: Activity, label: 'SOC Dashboard', href: '/' },
  { icon: Shield, label: 'Threat Intel', href: '/threats' },
  { icon: Network, label: 'Network Graph', href: '/network' },
  { icon: Cpu, label: 'Agent Fleet', href: '/agents' },
  { icon: AlertTriangle, label: 'Alerts', href: '/alerts' },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 flex-shrink-0 glass border-r border-slate-800/60 flex flex-col z-20 relative">
      <div className="h-16 flex items-center px-6 border-b border-slate-800/60">
        <div className="flex items-center gap-3 text-blue-500 font-bold text-xl tracking-wider">
          <Shield className="w-6 h-6" />
          <span>ARGUS</span>
        </div>
      </div>
      
      <nav className="flex-1 py-6 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                isActive 
                  ? "bg-blue-500/10 text-blue-400" 
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/50"
              )}
            >
              <item.icon className={cn("w-5 h-5", isActive ? "text-blue-500" : "")} />
              {item.label}
            </Link>
          )
        })}
      </nav>
      
      <div className="p-4 border-t border-slate-800/60">
        <Link
          to="/settings"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-400 hover:text-slate-100 transition-colors"
        >
          <Settings className="w-5 h-5" />
          Settings
        </Link>
      </div>
    </aside>
  )
}
