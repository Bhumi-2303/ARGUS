import {
  NetworkNode,
  NetworkConnection,
  Alert,
  Agent,
  ModelMetrics,
  Explanation,
  AuditEvent
} from '../types';

export const networkNodes: NetworkNode[] = [
  {
    id: 'node-hq-cc',
    name: 'Primary Control Center (GCC)',
    type: 'control-center',
    status: 'secure',
    position: { x: 0, y: 5, z: 0 },
    riskScore: 12,
    lastActivity: '2026-08-27T14:30:00Z',
    connectedAssets: ['node-sub-north', 'node-sub-south', 'node-scada-main']
  },
  {
    id: 'node-scada-main',
    name: 'Central SCADA Supervisory Host',
    type: 'scada',
    status: 'protected',
    position: { x: 2, y: 3, z: -1 },
    riskScore: 24,
    lastActivity: '2026-08-27T14:31:12Z',
    connectedAssets: ['node-hq-cc', 'node-hmi-ops1', 'node-sub-north', 'node-sub-west']
  },
  {
    id: 'node-sub-north',
    name: 'Substation North 500kV',
    type: 'substation',
    status: 'at-risk',
    position: { x: -6, y: 1, z: 4 },
    riskScore: 68,
    currentThreat: 'IEC-104 ASDU Injection Anomaly',
    lastActivity: '2026-08-27T14:32:05Z',
    connectedAssets: ['node-rtu-n1', 'node-ied-breaker1', 'node-scada-main']
  },
  {
    id: 'node-sub-south',
    name: 'Substation South 230kV',
    type: 'substation',
    status: 'secure',
    position: { x: 6, y: 1, z: 3 },
    riskScore: 18,
    lastActivity: '2026-08-27T14:29:45Z',
    connectedAssets: ['node-rtu-s1', 'node-ied-transformer', 'node-hq-cc']
  },
  {
    id: 'node-sub-west',
    name: 'Substation West Industrial Park',
    type: 'substation',
    status: 'compromised',
    position: { x: -8, y: -2, z: -5 },
    riskScore: 94,
    currentThreat: 'DDoS Command Flood & Unauthorized Setpoint Write',
    lastActivity: '2026-08-27T14:33:10Z',
    connectedAssets: ['node-plc-gen2', 'node-hmi-ops2', 'node-scada-main']
  },
  {
    id: 'node-rtu-n1',
    name: 'North Bus RTU-01',
    type: 'rtu',
    status: 'at-risk',
    position: { x: -8, y: 0, z: 6 },
    riskScore: 72,
    currentThreat: 'Unauthorized ASDU Frame Spooling',
    lastActivity: '2026-08-27T14:32:40Z',
    connectedAssets: ['node-sub-north', 'node-sensor-grid1']
  },
  {
    id: 'node-rtu-s1',
    name: 'South Feeder RTU-02',
    type: 'rtu',
    status: 'secure',
    position: { x: 8, y: 0, z: 5 },
    riskScore: 15,
    lastActivity: '2026-08-27T14:28:10Z',
    connectedAssets: ['node-sub-south']
  },
  {
    id: 'node-hmi-ops1',
    name: 'Operator Workstation HMI-01',
    type: 'hmi',
    status: 'protected',
    position: { x: 3, y: 4, z: -3 },
    riskScore: 28,
    lastActivity: '2026-08-27T14:31:50Z',
    connectedAssets: ['node-scada-main']
  },
  {
    id: 'node-hmi-ops2',
    name: 'Field Operations Terminal HMI-02',
    type: 'hmi',
    status: 'compromised',
    position: { x: -10, y: -3, z: -3 },
    riskScore: 91,
    currentThreat: 'Botnet C2 Communication',
    lastActivity: '2026-08-27T14:33:02Z',
    connectedAssets: ['node-sub-west']
  },
  {
    id: 'node-plc-gen2',
    name: 'Turbine Controller PLC-02',
    type: 'plc',
    status: 'compromised',
    position: { x: -12, y: -4, z: -7 },
    riskScore: 98,
    currentThreat: 'Firmware Override Attempt',
    lastActivity: '2026-08-27T14:33:15Z',
    connectedAssets: ['node-sub-west', 'node-sensor-turb']
  },
  {
    id: 'node-ied-breaker1',
    name: 'Feeder Breaker Protection IED',
    type: 'ied',
    status: 'secure',
    position: { x: -5, y: 2, z: 8 },
    riskScore: 22,
    lastActivity: '2026-08-27T14:27:30Z',
    connectedAssets: ['node-sub-north']
  },
  {
    id: 'node-ied-transformer',
    name: 'Main Transformer Differential IED',
    type: 'ied',
    status: 'protected',
    position: { x: 7, y: 2, z: 6 },
    riskScore: 10,
    lastActivity: '2026-08-27T14:30:15Z',
    connectedAssets: ['node-sub-south']
  },
  {
    id: 'node-sensor-grid1',
    name: 'Synchrophasor PMU Sensor-01',
    type: 'iot-sensor',
    status: 'at-risk',
    position: { x: -10, y: 1, z: 8 },
    riskScore: 65,
    currentThreat: 'Port Scan / Probe',
    lastActivity: '2026-08-27T14:32:00Z',
    connectedAssets: ['node-rtu-n1']
  },
  {
    id: 'node-sensor-turb',
    name: 'Vibration & Thermal Field Sensor',
    type: 'field-device',
    status: 'compromised',
    position: { x: -14, y: -5, z: -9 },
    riskScore: 89,
    currentThreat: 'Malformed Payload Injection',
    lastActivity: '2026-08-27T14:33:14Z',
    connectedAssets: ['node-plc-gen2']
  }
];

export const networkConnections: NetworkConnection[] = [
  { id: 'conn-1', sourceId: 'node-hq-cc', targetId: 'node-sub-north', trafficType: 'suspicious' },
  { id: 'conn-2', sourceId: 'node-hq-cc', targetId: 'node-sub-south', trafficType: 'normal' },
  { id: 'conn-3', sourceId: 'node-hq-cc', targetId: 'node-scada-main', trafficType: 'normal' },
  { id: 'conn-4', sourceId: 'node-scada-main', targetId: 'node-hmi-ops1', trafficType: 'normal' },
  { id: 'conn-5', sourceId: 'node-scada-main', targetId: 'node-sub-west', trafficType: 'suspicious' },
  { id: 'conn-6', sourceId: 'node-sub-north', targetId: 'node-rtu-n1', trafficType: 'suspicious' },
  { id: 'conn-7', sourceId: 'node-sub-north', targetId: 'node-ied-breaker1', trafficType: 'normal' },
  { id: 'conn-8', sourceId: 'node-sub-south', targetId: 'node-rtu-s1', trafficType: 'normal' },
  { id: 'conn-9', sourceId: 'node-sub-south', targetId: 'node-ied-transformer', trafficType: 'normal' },
  { id: 'conn-10', sourceId: 'node-sub-west', targetId: 'node-hmi-ops2', trafficType: 'suspicious' },
  { id: 'conn-11', sourceId: 'node-sub-west', targetId: 'node-plc-gen2', trafficType: 'suspicious' },
  { id: 'conn-12', sourceId: 'node-rtu-n1', targetId: 'node-sensor-grid1', trafficType: 'suspicious' },
  { id: 'conn-13', sourceId: 'node-plc-gen2', targetId: 'node-sensor-turb', trafficType: 'suspicious' }
];

export const alerts: Alert[] = [
  {
    id: 'ALT-2026-0891',
    severity: 'critical',
    attackType: 'IEC-104 ASDU SingleIOA Spooling Injection',
    source: '192.168.104.45 (External Malicious Spoofer)',
    target: 'Substation North 500kV (node-sub-north)',
    confidence: 0.98,
    riskScore: 96,
    timestamp: '2026-08-27T14:32:05Z',
    status: 'active'
  },
  {
    id: 'ALT-2026-0892',
    severity: 'critical',
    attackType: 'DDoS Control Command Flood',
    source: '10.200.4.120 (Botnet Ingress Node)',
    target: 'Substation West Industrial Park (node-sub-west)',
    confidence: 0.99,
    riskScore: 98,
    timestamp: '2026-08-27T14:33:10Z',
    status: 'active'
  },
  {
    id: 'ALT-2026-0893',
    severity: 'high',
    attackType: 'Unauthorized PLC Setpoint Overwrite',
    source: 'Field Operations Terminal HMI-02 (node-hmi-ops2)',
    target: 'Turbine Controller PLC-02 (node-plc-gen2)',
    confidence: 0.94,
    riskScore: 88,
    timestamp: '2026-08-27T14:33:02Z',
    status: 'investigating'
  },
  {
    id: 'ALT-2026-0894',
    severity: 'high',
    attackType: 'Reconnaissance & Sweep Scan',
    source: '172.16.88.9 (Unrecognized Gateway)',
    target: 'North Bus RTU-01 (node-rtu-n1)',
    confidence: 0.89,
    riskScore: 74,
    timestamp: '2026-08-27T14:32:40Z',
    status: 'investigating'
  },
  {
    id: 'ALT-2026-0895',
    severity: 'high',
    attackType: 'Botnet C2 Outbound Beaconing',
    source: 'Field Operations Terminal HMI-02 (node-hmi-ops2)',
    target: '185.220.101.5 (External C2 Server)',
    confidence: 0.96,
    riskScore: 82,
    timestamp: '2026-08-27T14:31:18Z',
    status: 'active'
  },
  {
    id: 'ALT-2026-0896',
    severity: 'medium',
    attackType: 'Synchrophasor PMU Port Probe',
    source: '192.168.104.90',
    target: 'Synchrophasor PMU Sensor-01 (node-sensor-grid1)',
    confidence: 0.76,
    riskScore: 58,
    timestamp: '2026-08-27T14:32:00Z',
    status: 'investigating'
  },
  {
    id: 'ALT-2026-0897',
    severity: 'medium',
    attackType: 'Supervisory U-Format Frame Flood',
    source: '10.200.4.15',
    target: 'North Bus RTU-01 (node-rtu-n1)',
    confidence: 0.82,
    riskScore: 64,
    timestamp: '2026-08-27T14:30:45Z',
    status: 'contained'
  },
  {
    id: 'ALT-2026-0898',
    severity: 'medium',
    attackType: 'Modbus Protocol Anomaly',
    source: '192.168.104.22',
    target: 'Turbine Controller PLC-02 (node-plc-gen2)',
    confidence: 0.79,
    riskScore: 55,
    timestamp: '2026-08-27T14:28:12Z',
    status: 'contained'
  },
  {
    id: 'ALT-2026-0899',
    severity: 'low',
    attackType: 'NTP Time Desynchronization Sweep',
    source: '192.168.1.5',
    target: 'Substation South 230kV (node-sub-south)',
    confidence: 0.65,
    riskScore: 32,
    timestamp: '2026-08-27T14:25:00Z',
    status: 'resolved'
  },
  {
    id: 'ALT-2026-0900',
    severity: 'low',
    attackType: 'Repeated ICMP Echo Ingress',
    source: '10.10.10.254',
    target: 'Central SCADA Supervisory Host (node-scada-main)',
    confidence: 0.58,
    riskScore: 20,
    timestamp: '2026-08-27T14:20:10Z',
    status: 'resolved'
  },
  {
    id: 'ALT-2026-0901',
    severity: 'critical',
    attackType: 'Man-In-The-Middle Intercept & Tamper',
    source: '10.200.4.199 (MitM Proxy)',
    target: 'Vibration & Thermal Field Sensor (node-sensor-turb)',
    confidence: 0.97,
    riskScore: 92,
    timestamp: '2026-08-27T14:33:14Z',
    status: 'active'
  },
  {
    id: 'ALT-2026-0902',
    severity: 'medium',
    attackType: 'Excessive Interrogation Polling Burst',
    source: '192.168.104.11',
    target: 'Substation North 500kV (node-sub-north)',
    confidence: 0.74,
    riskScore: 48,
    timestamp: '2026-08-27T14:22:30Z',
    status: 'resolved'
  }
];

export const agents: Agent[] = [
  {
    id: 'detection',
    name: 'Threat Detection Agent',
    status: 'active',
    currentTask: 'Ingesting IEC-104 telemetry stream & performing zero-shot evaluation',
    responsibilities: [
      'Real-time flow feature extraction & sequence classification',
      'Harmonized 4-tuple & 70-tuple feature vector parsing',
      'Multi-model inference execution (XGBoost, LightGBM, FT-Transformer)'
    ],
    input: ['Raw Network Telemetry Stream', 'IEC-104 ASDU/APDU Frames'],
    output: ['Raw Threat Alerts', 'Classification Probabilities', 'Anomaly Detection Events']
  },
  {
    id: 'risk',
    name: 'Risk Prioritization Agent',
    status: 'active',
    currentTask: 'Computing topological grid criticality & dynamic threat impact score',
    responsibilities: [
      'Grid asset topology mapping & impact assessment',
      'Bayesian prior-shift probability calibration',
      'Risk score computation based on asset criticality & threat severity'
    ],
    input: ['Raw Threat Alerts', 'Asset Inventory Topology', 'Prior Probabilities'],
    output: ['Prioritized Risk Scores', 'Critical Threat Queue', 'Asset Impact Vectors']
  },
  {
    id: 'explainability',
    name: 'SHAP & XAI Agent',
    status: 'active',
    currentTask: 'Generating feature attributions & vector retrieval for MITRE ATT&CK',
    responsibilities: [
      'TreeExplainer SHAP value calculation for model predictions',
      'Plain-language threat signature translation',
      'ChromaDB vector search against MITRE ATT&CK for ICS framework'
    ],
    input: ['Classification Events', 'Feature Importance Maps', 'Model Weights'],
    output: ['SHAP Contribution Bar Charts', 'MITRE Technique Mappings', 'XAI Narratives']
  },
  {
    id: 'response',
    name: 'Mitigation Response Agent',
    status: 'active',
    currentTask: 'Evaluating automated containment policy & VLAN isolation rules',
    responsibilities: [
      'Automated mitigation rule recommendation',
      'Firewall rule syntax generation (iptables/OpenFlow)',
      'Substation isolation & circuit breaker trip safeguards'
    ],
    input: ['Prioritized Risk Scores', 'Grid Topological Constraints'],
    output: ['Recommended Playbooks', 'Firewall Isolation Rules', 'Mitigation Commands']
  },
  {
    id: 'reporting',
    name: 'SOC Audit & Reporting Agent',
    status: 'idle',
    currentTask: 'Awaiting scheduled hourly compliance report generation',
    responsibilities: [
      'Immutable audit logging & chronological event sequencing',
      'NERC-CIP compliance metric aggregation',
      'Executive summary & SOC shift report compilation'
    ],
    input: ['System Audit Stream', 'Mitigation Logs', 'Agent Activity Feed'],
    output: ['NERC-CIP Compliance Reports', 'Incident Timelines', 'Executive Summaries']
  }
];

export const models: ModelMetrics[] = [
  {
    name: 'LightGBM',
    accuracy: 0.7936,
    precision: 0.9701,
    recall: 0.0838,
    f1: 0.4354,
    mcc: 0.2513,
    confidence: 0.94
  },
  {
    name: 'XGBoost',
    accuracy: 0.7207,
    precision: 0.7247,
    recall: 0.9919,
    f1: 0.8375,
    mcc: 0.3855,
    confidence: 0.89
  },
  {
    name: 'FT-Transformer',
    accuracy: 0.7892,
    precision: 0.9607,
    recall: 0.0849,
    f1: 0.4303,
    mcc: 0.2383,
    confidence: 0.91
  }
];

export const explanations: Explanation[] = [
  {
    alertId: 'ALT-2026-0891',
    prediction: 'IEC-104 ASDU SingleIOA Spooling Injection (Attack)',
    confidence: 0.98,
    model: 'LightGBM Native-70',
    features: [
      { feature: 'flow total IEC104_U_Message packets', contribution: +0.42 },
      { feature: 's_msg_ratio', contribution: -0.28 },
      { feature: 'flow packet APDU length mean', contribution: +0.18 },
      { feature: 'cot=6 (Activation)', contribution: +0.12 }
    ],
    narrative: 'High unnumbered control frame count combined with suppressed supervisory ACK ratio strongly indicates unauthorized ASDU command injection attempting to override substation relay states.'
  },
  {
    alertId: 'ALT-2026-0892',
    prediction: 'DDoS Control Command Flood (Attack)',
    confidence: 0.99,
    model: 'LightGBM Native-70',
    features: [
      { feature: 'total flow packets', contribution: +0.55 },
      { feature: 'flow duration', contribution: -0.22 },
      { feature: 'cmd_to_mon_ratio', contribution: +0.15 },
      { feature: 'tcp_flag_density', contribution: +0.08 }
    ],
    narrative: 'Massive burst of high-frequency command APDUs within a compressed time window, overwhelming the target substation gateway interface.'
  },
  {
    alertId: 'ALT-2026-0893',
    prediction: 'Unauthorized PLC Setpoint Overwrite (Attack)',
    confidence: 0.94,
    model: 'FT-Transformer Large',
    features: [
      { feature: 'type_id_process_control', contribution: +0.38 },
      { feature: 'cot=7 (Activation Confirm)', contribution: +0.26 },
      { feature: 'Fwd Header Len', contribution: +0.16 },
      { feature: 'Init Bwd Win Byts', contribution: -0.14 }
    ],
    narrative: 'Write-command ASDU targeted at turbine controller PLC with non-standard TCP window parameters originated from an unauthorized operational workstation node.'
  },
  {
    alertId: 'ALT-2026-0894',
    prediction: 'Reconnaissance & Sweep Scan (Suspicious)',
    confidence: 0.89,
    model: 'XGBoost Clean-CORAL',
    features: [
      { feature: 'tcp_flag_density', contribution: +0.48 },
      { feature: 'log_pkt_mean', contribution: -0.25 },
      { feature: 'pkt_mean_to_max', contribution: -0.16 }
    ],
    narrative: 'Sequential port probing targeting SCADA listening ports (TCP 2404 for IEC-104) identified from an unlisted internal gateway IP.'
  },
  {
    alertId: 'ALT-2026-0895',
    prediction: 'Botnet C2 Outbound Beaconing (Attack)',
    confidence: 0.96,
    model: 'LightGBM Native-70',
    features: [
      { feature: 'Flow IAT Min', contribution: -0.36 },
      { feature: 'log_pkt_max', contribution: +0.29 },
      { feature: 'fwd_pkt_ratio', contribution: +0.21 }
    ],
    narrative: 'Periodic fixed-interval outbound connections originating from HMI terminal attempting connection to known external C2 IP addresses.'
  }
];

export const auditEvents: AuditEvent[] = [
  {
    id: 'evt-1001',
    timestamp: '2026-08-27T14:33:15Z',
    agent: 'detection',
    message: 'Triggered critical threat classification for ALT-2026-0892 on Substation West Industrial Park.'
  },
  {
    id: 'evt-1002',
    timestamp: '2026-08-27T14:33:12Z',
    agent: 'risk',
    message: 'Recalculated grid risk vector; Substation West risk elevated to 94/100 (CRITICAL).'
  },
  {
    id: 'evt-1003',
    timestamp: '2026-08-27T14:33:05Z',
    agent: 'explainability',
    message: 'Computed TreeExplainer SHAP values & retrieved MITRE ATT&CK for ICS technique T0855 (Command Injection).'
  },
  {
    id: 'evt-1004',
    timestamp: '2026-08-27T14:33:00Z',
    agent: 'response',
    message: 'Proposed firewall isolation policy rule for node-sub-west ingress port TCP 2404.'
  },
  {
    id: 'evt-1005',
    timestamp: '2026-08-27T14:32:45Z',
    agent: 'system',
    message: 'Telemetry Kafka consumer rebalanced group argus-stream-consumer across 4 partitions.'
  },
  {
    id: 'evt-1006',
    timestamp: '2026-08-27T14:32:05Z',
    agent: 'detection',
    message: 'Detected IEC-104 ASDU frame anomaly (ALT-2026-0891) on Substation North 500kV.'
  },
  {
    id: 'evt-1007',
    timestamp: '2026-08-27T14:31:50Z',
    agent: 'risk',
    message: 'Prioritized North Bus RTU-01 threat severity (Risk Score: 72).'
  },
  {
    id: 'evt-1008',
    timestamp: '2026-08-27T14:30:00Z',
    agent: 'reporting',
    message: 'Generated hourly NERC-CIP compliance snapshot & network node health summary.'
  },
  {
    id: 'evt-1009',
    timestamp: '2026-08-27T14:28:10Z',
    agent: 'system',
    message: 'Substation South 230kV status verified SECURE following automated diagnostic check.'
  },
  {
    id: 'evt-1010',
    timestamp: '2026-08-27T14:25:00Z',
    agent: 'response',
    message: 'Resolved NTP time sync anomaly (ALT-2026-0899) via clock authority reset.'
  }
];
