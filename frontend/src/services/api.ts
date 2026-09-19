const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const API_TOKEN = import.meta.env.VITE_API_TOKEN || '';

const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${API_TOKEN}`,
});

export interface Incident {
  incident_id: string;
  event_id: string;
  created_at: string;
  updated_at: string;
  status: string;
  severity: string;
  asset: string;
  asset_criticality?: number;
  risk_score?: number;
  risk_tier?: string;
  detector_summary: string;
  knowledge_summary: string;
  decision?: any;
  response?: any;
  assigned_to?: string;
  approval_required: boolean;
  approval_status: string;
  approved_by?: string;
  approved_at?: string;
  approval_reason?: string;
  evidence_refs: string[];
  model_provenance?: any;
}

export interface TimelineEvent {
  event_id: string;
  timestamp: string;
  action: string;
  actor: string;
  details: string;
}

export interface SystemHealth {
  status: string;
  uptime: number;
  components: Record<string, ComponentHealth>;
  timestamp: string;
}

export interface ComponentHealth {
  name: string;
  healthy: boolean;
  status: string;
  details: any;
  last_checked: string;
}

export async function fetchIncidents(): Promise<Incident[]> {
  const response = await fetch(`${API_BASE_URL}/incidents/`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch incidents');
  const json = await response.json();
  return json.data;
}

export async function fetchIncident(id: string): Promise<Incident> {
  const response = await fetch(`${API_BASE_URL}/incidents/${id}`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch incident');
  const json = await response.json();
  return json.data;
}

export async function fetchIncidentTimeline(id: string): Promise<TimelineEvent[]> {
  const response = await fetch(`${API_BASE_URL}/incidents/${id}/timeline`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch timeline');
  const json = await response.json();
  return json.data;
}

export async function updateIncidentStatus(id: string, status: string, actor: string = "system"): Promise<Incident> {
  const response = await fetch(`${API_BASE_URL}/incidents/${id}/status`, {
    method: 'PATCH',
    headers: getHeaders(),
    body: JSON.stringify({ status, actor })
  });
  if (!response.ok) throw new Error('Failed to update status');
  const json = await response.json();
  return json.data;
}

export async function approveIncident(id: string, reason: string, actor: string = "system"): Promise<Incident> {
  const response = await fetch(`${API_BASE_URL}/incidents/${id}/approve`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ reason, actor })
  });
  if (!response.ok) throw new Error('Failed to approve incident');
  const json = await response.json();
  return json.data;
}

export async function fetchSystemHealth(): Promise<SystemHealth> {
  const response = await fetch(`${API_BASE_URL}/health`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch health');
  return response.json();
}
