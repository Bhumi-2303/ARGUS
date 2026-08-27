import React from 'react';
import { useParams } from 'react-router-dom';

export const AlertDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-text-primary tracking-tight">Alert Detail</h1>
      <div className="p-6 rounded-xl bg-bg-surface border border-border-muted text-text-secondary">
        <p className="font-mono text-sm">COMMAND / Alerts / {id || 'Detail'} Placeholder Page</p>
      </div>
    </div>
  );
};

export default AlertDetailPage;
