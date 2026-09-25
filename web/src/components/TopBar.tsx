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

export interface TopBarProps {
  sidebarCollapsed: boolean;
  selectedDomain: string;
  onSelectDomain: (domain: string) => void;
  apiConnected?: boolean;
}

export const DOMAINS = [
  { id: 'ciciot', name: 'Domain 1: CICIoT2023', subtitle: 'Source IoT Telemetry (5.49M)' },
  { id: 'nfton', name: 'Domain 2: NF-ToN-IoT-v2', subtitle: 'Target IoT Telemetry (8.41M)' },
  { id: 'iec104', name: 'Domain 3: IEC-104 SCADA', subtitle: 'Industrial Grid Protocol (2.29M)' },
];

export const TopBar: React.FC<TopBarProps> = ({
  sidebarCollapsed,
  selectedDomain,
  onSelectDomain,
  apiConnected = true,
}) => {
  const { theme, toggleTheme } = useTheme();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const activeDomain = DOMAINS.find((d) => d.id === selectedDomain) || DOMAINS[0];

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
            {DOMAINS.map((domain) => (
              <button
                key={domain.id}
                onClick={() => {
                  onSelectDomain(domain.id);
                  setDropdownOpen(false);
                }}
                className={clsx(
                  'w-full text-left px-3 py-2 rounded-lg text-xs font-mono transition-colors flex flex-col',
                  domain.id === selectedDomain
                    ? 'bg-cyan-500/10 text-cyan-300 font-semibold border border-cyan-500/30'
                    : 'text-slate-300 hover:bg-slate-800'
                )}
              >
                <span>{domain.name}</span>
                <span className="text-[10px] text-slate-500 font-normal">{domain.subtitle}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Right side: Badges & Actions */}
      <div className="flex items-center gap-4">
        {/* Research Prototype Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-mono font-medium">
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
          className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/80 text-slate-300 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-cyan-400" />}
        </button>
      </div>
    </header>
  );
};
