import React from 'react';
import { useParams } from 'react-router-dom';

export const AgentDetailPage: React.FC = () => {
  const { agentId } = useParams<{ agentId: string }>();

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-text-primary tracking-tight">Agent Detail</h1>
      <div className="p-6 rounded-xl bg-bg-surface border border-border-muted text-text-secondary">
        <p className="font-mono text-sm">AI SYSTEM / Pipeline & Agents / {agentId || 'Detail'} Placeholder Page</p>
      </div>
    </div>
  );
};

export default AgentDetailPage;
