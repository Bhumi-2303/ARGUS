export type Severity = 'critical' | 'high' | 'medium' | 'low';

export interface Alert {
  id: string;
  severity: Severity;
  status: string;
  attackType: string;
  source: string;
  target?: string;
  confidence?: number;
  riskScore: number;
  timestamp: string;
}

export interface FeatureImportance {
  feature: string;
  contribution: number;
}

export interface Explanation {
  alertId: string;
  prediction: string;
  model: string;
  confidence?: number;
  features: FeatureImportance[];
  narrative?: string;
}

export interface ModelMetrics {
  id: string;
  name: string;
  version: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  confidence?: number;
  mcc: number;
  status: string;
}

export type AgentId = string;

export interface AuditEvent {
  id: string;
  timestamp: string;
  agent: string;
  message: string;
}

export type NodeStatus = 'secure' | 'protected' | 'at-risk' | 'compromised';
export type NodeType = 'control-center' | 'scada' | 'substation' | 'hmi' | 'iot-sensor' | 'field-device' | 'rtu' | 'ied' | 'plc';

export interface NetworkNode {
  id: string;
  name: string;
  type: NodeType;
  status: NodeStatus;
  position: { x: number; y: number; z: number };
  connectedAssets: string[];
  riskScore: number;
  currentThreat?: string;
  lastActivity: string;
}

export interface NetworkConnection {
  id: string;
  sourceId: string;
  targetId: string;
  trafficType: string;
}
