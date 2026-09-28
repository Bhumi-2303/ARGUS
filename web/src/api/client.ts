/**
 * ARGUS Typed API Client
 * Single place for base URL configuration and FastAPI REST endpoints.
 */

export interface HealthResponse {
  status: string;
  models_loaded: Record<string, boolean>;
}

export interface DomainInfo {
  domain_id: string;
  name: string;
  full_name?: string;
  dataset?: string;
  num_records?: number;
  sample_size?: number;
  attack_ratio?: number;
  features: string[];
  status: string;
}


export interface DomainsResponse {
  count: number;
  domains: DomainInfo[];
}

export interface ModelProvenance {
  training_dataset: string;
  adaptation_method: string;
  features: string[];
  training_date?: string;
  threshold_selection?: string;
  seed?: number;
}


export interface ModelInfo {
  model_id: string;
  name: string;
  protocol_status: 'native' | 'coral_aligned' | 'dann_adapted' | string;
  threshold: number | null;
  source_domain: string;
  target_domain: string;
  status: string;
  provenance: ModelProvenance;
}

export interface ModelsResponse {
  count: number;
  models: ModelInfo[];
}

export interface ResultTableResponse {
  table_name: string;
  source_file?: string;
  protocol_status?: string;
  row_count: number;
  diagnostic_only: boolean;
  data: Record<string, any>[];
}

export interface PredictRequest {
  model_name: string;
  features: {
    pkt_mean_to_max: number;
    tcp_flag_density: number;
    log_pkt_mean: number;
    log_pkt_max: number;
  };
}

export interface PredictResponse {
  model_name: string;
  probability: number;
  prediction: number;
  threshold: number;
  features: Record<string, number>;
}

export interface FeatureShiftMetric {
  feature: string;
  ks_statistic: number;
  ks_pvalue: number;
  psi_statistic: number;
  shift_detected: boolean;
}

export interface ShiftResponse {
  target_domain: string;
  reference_domain?: string;
  window_size?: number;
  ks_threshold?: number;
  psi_threshold?: number;
  domain_shift: boolean;
  feature_shifts: FeatureShiftMetric[];
}

export interface ExplainRequest {
  model_name: string;
  features: {
    pkt_mean_to_max: number;
    tcp_flag_density: number;
    log_pkt_mean: number;
    log_pkt_max: number;
  };
}

export interface ExplainResponse {
  base_value: number;
  shap_values: Record<string, number>;
  top_feature: string;
  top_feature_impact: number;
}

export interface OnboardRequest {
  target_domain: string;
  adaptation_window_size: number;
  calibration_window_size: number;
  test_window_size: number;
}

export interface OnboardMetrics {
  accuracy: number;
  f1_score: number;
  mcc: number;
  fpr: number;
  fnr: number;
}

export interface OnboardResponse {
  target_domain: string;
  demo_scale: boolean;
  coral_fitted: boolean;
  selected_threshold: number;
  metrics: OnboardMetrics;
  evaluated_test_size: number;
}

export interface TopologyNode {
  id: string;
  name: string;
  type: 'bus' | 'gateway' | 'engine' | 'agent' | string;
  responsibility: string;
  status: 'idle' | 'busy' | 'blocked' | 'failed' | string;
  implementation_type: 'full' | 'stub' | string;
  layer: 'center' | 'inner' | 'outer' | string;
}

export interface TopologyEdge {
  source: string;
  target: string;
  label: string;
  event_types: string[];
}

export interface TopologyResponse {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
}

export interface FlowEventItem {
  event_id: string;
  correlation_id: string;
  source_node: string;
  target_node: string;
  event_type: string;
  timestamp: string;
  summary: string;
  payload: Record<string, any>;
}

export interface SimulateFlowResponse {
  correlation_id: string;
  flow_status: string;
  total_events: number;
  events: FlowEventItem[];
}

export interface TestCaseItem {
  id: string;
  name: string;
  domain: string;
  domain_name: string;
  ground_truth_label: number;
  ground_truth_class: string;
  features: {
    pkt_mean_to_max: number;
    tcp_flag_density: number;
    log_pkt_mean: number;
    log_pkt_max: number;
  };
  provenance: string;
}

export interface SampleItem {
  id: string;
  description: string;
  domain: string;
  ground_truth_label: number;
  ground_truth_class: string;
  features: {
    pkt_mean_to_max: number;
    tcp_flag_density: number;
    log_pkt_mean: number;
    log_pkt_max: number;
  };
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error ${res.status}: ${errorText || res.statusText}`);
  }

  return res.json();
}

export const api = {
  // Health
  getHealth: () => fetchJson<HealthResponse>('/health'),

  // Domains
  getDomains: () => fetchJson<DomainsResponse>('/api/v1/domains'),

  // Models
  getModels: () => fetchJson<ModelsResponse>('/api/v1/models'),

  // Results (Verified / Diagnostic CSVs)
  getResultTable: (tableName: string) =>
    fetchJson<ResultTableResponse>(`/api/v1/results/${tableName}`),

  // Predict
  predict: (data: PredictRequest) =>
    fetchJson<PredictResponse>('/api/v1/predict', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Shift Analysis
  getShift: (domain = 'nfton', windowSize = 1000) =>
    fetchJson<ShiftResponse>(`/api/v1/shift?domain=${domain}&window_size=${windowSize}`),

  // SHAP Explainability
  explain: (data: ExplainRequest) =>
    fetchJson<ExplainResponse>('/api/v1/explain', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Verified Test Cases
  getTestCases: () => fetchJson<TestCaseItem[]>('/api/v1/data/test-cases'),

  // Verified Dataset Samples
  getSamples: () => fetchJson<SampleItem[]>('/api/v1/data/samples'),

  // Agent Topology
  getTopology: () => fetchJson<TopologyResponse>('/api/v1/agents/topology'),

  // Agent Flow Trace
  simulateFlow: () => fetchJson<SimulateFlowResponse>('/api/v1/agents/trace', { method: 'POST' }),

  // Agent WebSocket Stream Helper
  getAgentStreamWsUrl: () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const base = API_BASE_URL ? API_BASE_URL.replace(/^http/, 'ws') : `${protocol}//${host}`;
    return `${base}/api/v1/agents/stream`;
  },

  // SSE Stream URL Helper
  getStreamUrl: (domain = 'nfton', models = 'model_d2_coral,xgb_source', speed = 10, seed = 42) =>
    `${API_BASE_URL}/api/v1/stream?domain=${domain}&models=${encodeURIComponent(models)}&speed=${speed}&seed=${seed}`,
};



