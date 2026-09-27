import React, { useState, Suspense } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { ErrorBoundary } from './ErrorBoundary';
import { Skeleton } from './Skeleton';
import { Footer } from './Footer';
import { clsx } from 'clsx';

export interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState('ciciot');

  const { data: healthData, isError: isHealthError } = useQuery({
    queryKey: ['health'],
    queryFn: api.getHealth,
    refetchInterval: 5000,
    retry: false
  });
  const apiConnected = healthData?.status === 'healthy' && !isHealthError;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col antialiased">
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* TopBar */}
      <TopBar
        sidebarCollapsed={sidebarCollapsed}
        selectedDomain={selectedDomain}
        onSelectDomain={setSelectedDomain}
        apiConnected={apiConnected}
      />

      {/* Main Content Area */}
      <main
        className={clsx(
          'flex-1 pt-20 px-6 pb-12 transition-all duration-300',
          sidebarCollapsed ? 'ml-16' : 'ml-64'
        )}
      >
        <div className="max-w-7xl mx-auto space-y-6">
          <ErrorBoundary>
            <Suspense
              fallback={
                <div className="space-y-6 p-6">
                  <Skeleton variant="card" />
                  <Skeleton variant="table" />
                </div>
              }
            >
              {children}
            </Suspense>
          </ErrorBoundary>
        </div>
        <Footer />
      </main>
    </div>
  );
};
