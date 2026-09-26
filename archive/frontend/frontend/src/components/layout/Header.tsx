import React, { useState, useEffect } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { Bell, ShieldCheck, User, Clock, ChevronRight } from 'lucide-react';

export const Header: React.FC = () => {
  const location = useLocation();
  const params = useParams();
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  const getBreadcrumbsAndTitle = () => {
    const path = location.pathname;
    if (path === '/') {
      return { group: 'COMMAND', title: 'Overview', breadcrumbs: ['COMMAND', 'Overview'] };
    }
    if (path === '/alerts') {
      return { group: 'COMMAND', title: 'Alerts & Incidents', breadcrumbs: ['COMMAND', 'Alerts'] };
    }
    if (path.startsWith('/alerts/')) {
      const alertId = params.id || 'Detail';
      return { group: 'COMMAND', title: `Alert Detail (${alertId})`, breadcrumbs: ['COMMAND', 'Alerts', alertId] };
    }
    if (path === '/network') {
      return { group: 'COMMAND', title: 'Network Topology & Grid Map', breadcrumbs: ['COMMAND', 'Network'] };
    }
    if (path === '/pipeline') {
      return { group: 'AI SYSTEM', title: 'Pipeline & Multi-Agent Architecture', breadcrumbs: ['AI SYSTEM', 'Pipeline'] };
    }
    if (path.startsWith('/pipeline/')) {
      const agentId = params.agentId || 'Agent';
      return { group: 'AI SYSTEM', title: `Agent Detail (${agentId})`, breadcrumbs: ['AI SYSTEM', 'Pipeline', agentId] };
    }
    if (path === '/models') {
      return { group: 'AI SYSTEM', title: 'Model Metrics & Performance', breadcrumbs: ['AI SYSTEM', 'Models'] };
    }
    if (path === '/explainability') {
      return { group: 'AI SYSTEM', title: 'XAI & SHAP Explainability', breadcrumbs: ['AI SYSTEM', 'Explainability'] };
    }
    if (path === '/reports') {
      return { group: 'OPERATIONS', title: 'Compliance & Incident Reports', breadcrumbs: ['OPERATIONS', 'Reports'] };
    }
    if (path === '/settings') {
      return { group: 'OPERATIONS', title: 'System Settings & Configurations', breadcrumbs: ['OPERATIONS', 'Settings'] };
    }
    return { group: 'ARGUS', title: 'SOC Dashboard', breadcrumbs: ['ARGUS', 'Dashboard'] };
  };

  const { title, breadcrumbs } = getBreadcrumbsAndTitle();

  return (
    <header className="h-16 bg-bg-surface border-b border-border-muted px-6 flex items-center justify-between flex-shrink-0 z-10">
      {/* Left: Breadcrumbs & Dynamic Title */}
      <div className="flex flex-col">
        <div className="flex items-center gap-1.5 text-xs text-text-secondary font-mono">
          {breadcrumbs.map((crumb, idx) => (
            <React.Fragment key={idx}>
              {idx > 0 && <ChevronRight className="w-3 h-3 text-text-secondary/50" />}
              <span className={idx === breadcrumbs.length - 1 ? 'text-info font-medium' : ''}>
                {crumb}
              </span>
            </React.Fragment>
          ))}
        </div>
        <h1 className="text-lg font-bold text-text-primary tracking-tight leading-none mt-1">
          {title}
        </h1>
      </div>

      {/* Right: Status Pill, Clock, Notifications, User Profile */}
      <div className="flex items-center gap-4">
        {/* Operational Status Pill */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-safe/10 border border-safe/30 text-safe text-xs font-mono font-semibold glow-safe">
          <ShieldCheck className="w-4 h-4 text-safe" />
          <span>SYSTEM OPERATIONAL • DEFENSIVE LEVEL 1</span>
        </div>

        {/* Live Clock */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-bg-surface-raised border border-border-muted text-text-secondary text-xs font-mono">
          <Clock className="w-3.5 h-3.5 text-info" />
          <span>{timeStr || '14:35:00 UTC'}</span>
        </div>

        {/* Notification Bell */}
        <button
          className="relative p-2 rounded-lg bg-bg-surface-raised border border-border-muted text-text-secondary hover:text-text-primary hover:border-info/40 transition-colors"
          title="Notifications & Alerts"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-critical text-[10px] font-bold font-mono text-text-primary flex items-center justify-center glow-critical">
            3
          </span>
        </button>

        {/* User Profile */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-border-muted">
          <div className="p-2 rounded-lg bg-bg-surface-raised border border-border-muted text-text-primary">
            <User className="w-4 h-4 text-info" />
          </div>
          <div className="hidden sm:flex flex-col text-left">
            <span className="text-xs font-semibold text-text-primary leading-tight">
              SOC Analyst
            </span>
            <span className="text-[10px] text-text-secondary font-mono leading-tight">
              Operator-01
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
