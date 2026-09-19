import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Globe, ShieldAlert, Cpu, FileText, type LucideIcon } from 'lucide-react';
import {
  Shield,
  Activity,
  Server,
  BarChart2,
  HeartPulse,
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: LucideIcon;
}

interface NavGroup {
  groupName: string;
  items: NavItem[];
}


const navGroups: NavGroup[] = [
  {
    groupName: 'OPERATIONS',
    items: [
      { name: 'Command Center', path: '/', icon: Activity },
      { name: 'Incidents & Alerts', path: '/alerts', icon: ShieldAlert },
      { name: 'Asset Intelligence', path: '/assets', icon: Server },
      { name: 'Network Topology', path: '/network', icon: Globe }
    ]
  },
  {
    groupName: 'INTELLIGENCE',
    items: [
      { name: 'Explainability (XAI)', path: '/explainability', icon: Cpu },
      { name: 'Audit Reports', path: '/reports', icon: FileText }
    ]
  },
  {
    groupName: 'SYSTEM',
    items: [
      { name: 'Analytics', path: '/analytics', icon: BarChart2 },
      { name: 'Health', path: '/health', icon: HeartPulse }
    ]
  }
];


export const Sidebar: React.FC = () => {
  const location = useLocation();

  const isLinkActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <aside className="w-64 flex-shrink-0 bg-slate-900 border-r border-slate-800 flex flex-col z-20 h-screen select-none">
      <div className="h-16 px-6 flex items-center border-b border-slate-800 bg-slate-900/50">
        <NavLink to="/" className="flex items-center gap-3 group">
          <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20 group-hover:border-blue-500/50 transition-colors">
            <Shield className="w-5 h-5 text-blue-500" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 font-bold tracking-widest text-slate-100 text-lg leading-none">
              ARGUS
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-500 font-mono uppercase tracking-normal">
                SOC
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono tracking-wider mt-1">
              OPERATIONS CENTER
            </p>
          </div>
        </NavLink>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
        {navGroups.map((group) => (
          <div key={group.groupName} className="space-y-1">
            <h3 className="px-3 text-[11px] font-mono font-semibold tracking-wider text-slate-500 uppercase">
              {group.groupName}
            </h3>
            <div className="mt-2 space-y-0.5">
              {group.items.map((item) => {
                const active = isLinkActive(item.path);
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                      active
                        ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30 shadow-sm font-semibold'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${active ? 'text-blue-400' : 'text-slate-400'}`} />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
