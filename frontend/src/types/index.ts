export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low';

export interface Alert {
  id: string;
  severity: AlertSeverity;
  name: string;
  source: string;
  target: string;
  confidence: number;
  timestamp: string;
}

export interface AttackCategory {
  name: string;
  count: number;
  color: string;
}

export interface ModelPerformance {
  name: string;
  confidence: number;
  color: string;
}

export interface AttackTrend {
  time: string;
  volume: number;
  isPeak?: boolean;
}

export interface AgentStatus {
  id: string;
  name: string;
  status: 'Active' | 'Inactive';
  uptime: number;
  stage: string;
  icon: any; // Lucide icon
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
}

export type AgentId = 'ag-detect' | 'ag-assess' | 'ag-explain' | 'ag-respond' | 'ag-report';

export interface Agent {
  id: AgentId;
  name: string;
  roleSummary: string;
  status: 'Active' | 'Inactive';
  currentTask: string;
  responsibilities: string[];
  input: string[];
  processing: string;
  output: string[];
  receivesFrom: AgentId | 'Network Traffic';
  sendsTo: AgentId | 'Audit Trail' | 'ag-detect'; // for reporting feedback
  executionTrace: { timestamp: string; step: string }[];
}

export interface ModelMetrics {
  id: string;
  name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  mcc: number;
  fpr: number;
  fnr: number;
}
