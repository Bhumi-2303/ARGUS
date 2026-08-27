export type NodeStatus = 'secure' | 'at-risk' | 'compromised' | 'protected';

export type NodeType =
  | 'control-center'
  | 'substation'
  | 'rtu'
  | 'iot-sensor'
  | 'hmi'
  | 'plc'
  | 'scada'
  | 'ied'
  | 'field-device';

export interface NetworkNode {
  id: string;
  name: string;
  type: NodeType;
  status: NodeStatus;
  position: { x: number; y: number; z: number };
  riskScore: number;
  currentThreat?: string;
  lastActivity: string;
  connectedAssets: string[];
}

export interface NetworkConnection {
  id: string;
  sourceId: string;
  targetId: string;
  trafficType: 'normal' | 'suspicious';
}

export type Severity = 'critical' | 'high' | 'medium' | 'low';

export interface Alert {
  id: string;
  severity: Severity;
  attackType: string;
  source: string;
  target: string;
  confidence: number;
  riskScore: number;
  timestamp: string;
  status: 'active' | 'investigating' | 'contained' | 'resolved';
}

export type AgentId = 'detection' | 'risk' | 'explainability' | 'response' | 'reporting';

export interface Agent {
  id: AgentId;
  name: string;
  status: 'active' | 'idle' | 'error';
  currentTask?: string;
  responsibilities: string[];
  input: string[];
  output: string[];
}

export interface ModelMetrics {
  name: 'XGBoost' | 'LightGBM' | 'FT-Transformer';
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  mcc: number;
  confidence: number;
}

export interface ShapFeature {
  feature: string;
  contribution: number;
}

export interface Explanation {
  alertId: string;
  prediction: string;
  confidence: number;
  model: string;
  features: ShapFeature[];
  narrative: string;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  agent: AgentId | 'system';
  message: string;
}
