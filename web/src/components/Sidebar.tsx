import React from 'react';
import { NavLink } from 'react-router-dom';
import { PAGES, PageDefinition } from '../app/pages';
import { Shield, ChevronLeft, ChevronRight, Cpu } from 'lucide-react';
import { clsx } from 'clsx';

export interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  // Group pages by category
  const categories = Array.from(new Set(PAGES.map((p) => p.category)));

  return (
    <aside
      className={clsx(
        'fixed top-0 left-0 z-40 h-screen transition-all duration-300 bg-slate-900 border-r border-slate-800 flex flex-col',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Brand Header */}
      <div className="h-16 px-4 flex items-center justify-between border-b border-slate-800/80">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="p-2 rounded bg-blue-600 text-white shrink-0">
            <Shield className="w-5 h-5" />
          </div>
          {!collapsed && (
            <div>
              <h1 className="text-base font-extrabold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-1.5 font-mono">
                ARGUS
                <span className="text-[10px] font-normal px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  v1.0
                </span>
              </h1>
              <p className="text-[10px] text-slate-400 truncate max-w-[140px]">
                Autonomous Grid Security
              </p>
            </div>
          )}
        </div>

        <button
          onClick={onToggle}
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-800 transition-colors"
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {categories.map((cat) => {
          const categoryPages = PAGES.filter((p) => p.category === cat);
          return (
            <div key={cat} className="space-y-1">
              {!collapsed && (
                <h4 className="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">
                  {cat}
                </h4>
              )}
              <div className="space-y-0.5">
                {categoryPages.map((page) => {
                  const Icon = page.icon;
                  return (
                    <NavLink
                      key={page.id}
                      to={page.path}
                      end={page.path === '/'}
                      className={({ isActive }) =>
                        clsx(
                          'flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 group relative',
                          isActive
                            ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 shadow-md shadow-cyan-500/10'
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                        )
                      }
                      title={collapsed ? page.title : undefined}
                    >
                      <Icon className="w-4 h-4 shrink-0" />
                      {!collapsed && (
                        <div className="flex items-center justify-between flex-1 truncate">
                          <span className="truncate">{page.title}</span>
                          {page.badge && (
                            <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300">
                              {page.badge}
                            </span>
                          )}
                        </div>
                      )}
                    </NavLink>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Sidebar Footer */}
      {!collapsed && (
        <div className="p-3 border-t border-slate-800 text-[11px] text-slate-500 font-mono flex items-center justify-between bg-slate-950/40">
          <span className="flex items-center gap-1">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" /> SCADA / ICS Security
          </span>
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
            MIT
          </span>
        </div>
      )}
    </aside>
  );
};
