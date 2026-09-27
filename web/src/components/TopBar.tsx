import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { StatusPill } from './StatusPill';
import {
  Sun,
  Moon,
  Globe,
  Activity,
  Beaker,
  ChevronDown,
} from 'lucide-react';
import { clsx } from 'clsx';
import { useQuery } from '@tanstack/react-query';
import { api, DomainInfo } from '../api/client';

export interface TopBarProps {
  sidebarCollapsed: boolean;
  selectedDomain: string;
  onSelectDomain: (domain: string) => void;
  apiConnected?: boolean;
}



export const TopBar: React.FC<TopBarProps> = ({
  sidebarCollapsed,
  selectedDomain,
  onSelectDomain,
  apiConnected = true,
}) => {
  const { theme, toggleTheme } = useTheme();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const { data: domainsData } = useQuery({
    queryKey: ['domains'],
    queryFn: api.getDomains,
  });
  const domains = domainsData?.domains || [];
  const activeDomain = domains.find((d) => d.domain_id === selectedDomain) || domains[0] || { name: 'Loading...' };


  return (
    <header
      className={clsx(
        'fixed top-0 right-0 z-30 h-16 transition-all duration-300 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 flex items-center justify-between px-6',
        sidebarCollapsed ? 'left-16' : 'left-64'
      )}
    >
      {/* Left side: Domain Selector Dropdown */}
      <div className="relative">
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/80 hover:bg-slate-800 text-xs font-mono font-medium text-slate-200 transition-colors"
        >
          <Globe className="w-4 h-4 text-cyan-400" />
          <span>{activeDomain.name}</span>
          <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
        </button>

        {dropdownOpen && (
          <div
            onMouseLeave={() => setDropdownOpen(false)}
            className="absolute left-0 top-full mt-2 z-50 w-72 p-1.5 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl space-y-1 animate-in fade-in duration-150"
          >
            <div className="px-3 py-1.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">
              Active Telemetry Domain
            </div>
            {domains.map((domain) => (
              <button
                key={domain.domain_id}
                onClick={() => {
                  if (domain.status === 'verified') {
                    onSelectDomain(domain.domain_id);
                    setDropdownOpen(false);
                  }
                }}
                disabled={domain.status !== 'verified'}
                title={domain.status === 'planned' ? 'Not yet backed by a verified result' : domain.status === 'partial' ? 'Partially verified - see Protocol & Limits' : ''}
                className={clsx(
                  'w-full text-left px-3 py-2 rounded-lg text-xs font-mono transition-colors flex flex-col',
                  domain.domain_id === selectedDomain
                    ? 'bg-cyan-500/10 text-cyan-300 font-semibold border border-cyan-500/30'
                    : domain.status !== 'verified' 
                    ? 'text-slate-500 opacity-50 cursor-not-allowed'
                    : 'text-slate-300 hover:bg-slate-800'
                )}
              >
                <span>{domain.name} {domain.status !== 'verified' && `(${domain.status})`}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Right side: Badges & Actions */}
      <div className="flex items-center gap-4">
        {/* Research Prototype Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded bg-blue-500/10 border border-blue-500/30 text-blue-700 dark:text-blue-300 text-xs font-mono font-medium">
          <Beaker className="w-3.5 h-3.5 text-purple-400" />
          <span>RESEARCH PROTOTYPE</span>
        </div>

        {/* Connection Status Indicator */}
        <StatusPill
          status={apiConnected ? 'healthy' : 'reconnecting'}
          label={apiConnected ? 'API Connected' : 'Connecting'}
        />

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/80 text-slate-300 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-800 transition-colors"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-cyan-400" />}
        </button>
      </div>
    </header>
  );
};
