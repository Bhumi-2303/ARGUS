import {
  NetworkNode,
  NetworkConnection,
  Alert,
  Agent,
  AgentId,
  ModelMetrics,
  Explanation,
  AuditEvent
} from '../types';
import {
  networkNodes,
  networkConnections,
  alerts,
  agents,
  models,
  explanations,
  auditEvents
} from '../data/mockData';

// Simulated API latency helper
const delay = <T>(data: T, ms = 150): Promise<T> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(data), ms);
  });
};

/**
 * Network Nodes & Topology APIs
 */
export async function getNetworkNodes(): Promise<NetworkNode[]> {
  return delay(networkNodes);
}

export async function getNetworkNodeById(id: string): Promise<NetworkNode | undefined> {
  const node = networkNodes.find((n) => n.id === id);
  return delay(node);
}

export async function getNetworkConnections(): Promise<NetworkConnection[]> {
  return delay(networkConnections);
}

/**
 * Alerts & Incident Response APIs
 */
export async function getAlerts(): Promise<Alert[]> {
  return delay(alerts);
}

export async function getAlertById(id: string): Promise<Alert | undefined> {
  const alert = alerts.find((a) => a.id === id);
  return delay(alert);
}

/**
 * AI Agents & Pipeline APIs
 */
export async function getAgents(): Promise<Agent[]> {
  return delay(agents);
}

export async function getAgentById(id: AgentId): Promise<Agent | undefined> {
  const agent = agents.find((a) => a.id === id);
  return delay(agent);
}

/**
 * Machine Learning Models & Metrics APIs
 */
export async function getModels(): Promise<ModelMetrics[]> {
  return delay(models);
}

/**
 * XAI & SHAP Explanation APIs
 */
export async function getExplanations(): Promise<Explanation[]> {
  return delay(explanations);
}

export async function getExplanationByAlertId(alertId: string): Promise<Explanation | undefined> {
  const exp = explanations.find((e) => e.alertId === alertId);
  return delay(exp);
}

/**
 * Audit Events & Activity Stream APIs
 */
export async function getAuditEvents(): Promise<AuditEvent[]> {
  return delay(auditEvents);
}
