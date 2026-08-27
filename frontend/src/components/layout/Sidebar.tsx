import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  Shield,
  Activity,
  ShieldAlert,
  Network,
  Cpu,
  BrainCircuit,
  Sparkles,
  FileText,
  Settings
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
}

interface NavGroup {
  groupName: string;
  items: NavItem[];
}

const navGroups: NavGroup[] = [
  {
    groupName: 'COMMAND',
    items: [
      { name: 'Overview', path: '/', icon: Activity },
      { name: 'Alerts', path: '/alerts', icon: ShieldAlert },
      { name: 'Network', path: '/network', icon: Network }
    ]
  },
  {
    groupName: 'AI SYSTEM',
    items: [
      { name: 'Pipeline & Agents', path: '/pipeline', icon: Cpu },
      { name: 'Models', path: '/models', icon: BrainCircuit },
      { name: 'Explainability', path: '/explainability', icon: Sparkles }
    ]
  },
  {
    groupName: 'OPERATIONS',
    items: [
      { name: 'Reports', path: '/reports', icon: FileText },
      { name: 'Settings', path: '/settings', icon: Settings }
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
    <aside className="w-64 flex-shrink-0 bg-bg-surface border-r border-border-muted flex flex-col z-20 h-screen select-none">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center border-b border-border-muted bg-bg-surface-raised/40">
        <NavLink to="/" className="flex items-center gap-3 group">
          <div className="p-2 rounded-lg bg-info/10 border border-info/20 group-hover:border-info/50 transition-colors glow-info">
            <Shield className="w-5 h-5 text-info" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 font-bold tracking-widest text-text-primary text-lg leading-none">
              ARGUS
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-info/20 text-info font-mono uppercase tracking-normal">
                v2.0
              </span>
            </div>
            <p className="text-[10px] text-text-secondary font-mono tracking-wider mt-1">
              GRID CYBER DEFENSE SOC
            </p>
          </div>
        </NavLink>
      </div>

      {/* Navigation Groups */}
      <nav className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
        {navGroups.map((group) => (
          <div key={group.groupName} className="space-y-1">
            <h3 className="px-3 text-[11px] font-mono font-semibold tracking-wider text-text-secondary/70 uppercase">
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
                        ? 'bg-info/10 text-info border border-info/30 shadow-sm font-semibold'
                        : 'text-text-secondary hover:text-text-primary hover:bg-bg-surface-raised/60'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${active ? 'text-info' : 'text-text-secondary'}`} />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* System Status Footer */}
      <div className="p-4 border-t border-border-muted bg-bg-surface-raised/30">
        <div className="flex items-center justify-between text-xs">
          <span className="text-text-secondary font-mono">FRAMEWORK</span>
          <span className="text-safe font-mono font-semibold flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-safe animate-pulse glow-safe" />
            DEFENSIVE ONLINE
          </span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
