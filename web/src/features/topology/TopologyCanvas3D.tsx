import React, { useRef, useMemo, useState, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import {
  Cpu,
  Database,
  Crosshair,
  BarChart3,
  BookOpen,
  AlertTriangle,
  ShieldCheck,
  Radio,
  Zap,
  Lock,
  Workflow,
  CheckCircle,
  XCircle,
  MinusCircle,
  Play,
  RotateCcw,
} from 'lucide-react';
import { TopologyNode, TopologyEdge, FlowEventItem, ShiftPCAResponse } from '../../api/client';

export type SceneMode = 'TOPOLOGY' | 'DOMAIN_SHIFT' | 'SHAP' | 'DECISION_TIMELINE';
export type NodeState = 'idle' | 'running' | 'success' | 'skipped' | 'failed';

export interface TopologyCanvas3DProps {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  selectedNode: TopologyNode | null;
  onSelectNode: (node: TopologyNode) => void;
  activeEvents: FlowEventItem[];
  layoutMode?: 'architecture' | 'topology';
  sceneMode?: SceneMode;
  quality?: 'high' | 'low';
  reducedMotion?: boolean;
  shiftData?: ShiftPCAResponse | null;
  shiftLoading?: boolean;
  selectedIncident?: any;
  flowFeatures?: Record<string, number>;
  flowExplanation?: {
    shap_values: Record<string, number>;
    top_feature: string;
    top_feature_impact: number;
    base_value: number;
  };
  nodeStatusMap?: Record<string, NodeState>;
  onApproveIncident?: (incidentId: string) => void;
}

// Visual theme configurations
function getAgentVisualConfig(nodeId: string, nodeType: string) {
  switch (nodeId.toLowerCase()) {
    case 'orchestrator':
      return {
        color: '#00f0ff',
        accent: '#818cf8',
        icon: Workflow,
        label: 'ARGUS Orchestrator',
        subtitle: 'Central Workflow Engine',
        radius: 2.2,
      };
    case 'data_intelligence':
      return {
        color: '#06b6d4',
        accent: '#38bdf8',
        icon: Database,
        label: 'Data Intelligence',
        subtitle: 'Harmonization & Loader',
        radius: 1.5,
      };
    case 'threat_analysis':
      return {
        color: '#f43f5e',
        accent: '#fb7185',
        icon: Crosshair,
        label: 'Threat Analysis',
        subtitle: 'CORAL Adapted ML Inference',
        radius: 1.5,
      };
    case 'explainability':
      return {
        color: '#a855f7',
        accent: '#c084fc',
        icon: BarChart3,
        label: 'Explainability',
        subtitle: 'TreeSHAP Attributions',
        radius: 1.5,
      };
    case 'knowledge_context':
      return {
        color: '#3b82f6',
        accent: '#60a5fa',
        icon: BookOpen,
        label: 'Knowledge Context',
        subtitle: 'MITRE ATT&CK & CVEs',
        radius: 1.5,
      };
    case 'risk_prediction':
      return {
        color: '#f59e0b',
        accent: '#fbbf24',
        icon: AlertTriangle,
        label: 'Risk Prediction',
        subtitle: 'Grid Criticality Assessment',
        radius: 1.5,
      };
    case 'decision_support':
      return {
        color: '#10b981',
        accent: '#34d399',
        icon: ShieldCheck,
        label: 'Decision Support',
        subtitle: 'Automated Containment',
        radius: 1.5,
      };
    case 'api_gateway':
      return {
        color: '#38bdf8',
        accent: '#7dd3fc',
        icon: Radio,
        label: 'API Gateway',
        subtitle: 'Entrypoint & WebSocket Bus',
        radius: 1.6,
      };
    case 'message_bus':
      return {
        color: '#00f0ff',
        accent: '#38bdf8',
        icon: Zap,
        label: 'Message Bus',
        subtitle: 'Pub-Sub Event Broker',
        radius: 1.6,
      };
    case 'policy_engine':
      return {
        color: '#6366f1',
        accent: '#a5b4fc',
        icon: Lock,
        label: 'Policy Engine',
        subtitle: 'Zero Trust Guardrails',
        radius: 1.5,
      };
    default:
      return {
        color: '#38bdf8',
        accent: '#94a3b8',
        icon: Cpu,
        label: nodeId,
        subtitle: nodeType,
        radius: 1.4,
      };
  }
}

// -------------------------------------------------------------
// 1. Instanced Particle Edge Conduits
// -------------------------------------------------------------
interface ParticleEdgeProps {
  sourcePos: [number, number, number];
  targetPos: [number, number, number];
  color: string;
  isActive: boolean;
  particleCount?: number;
  reducedMotion?: boolean;
}

function InstancedParticleEdge({
  sourcePos,
  targetPos,
  color,
  isActive,
  particleCount = 12,
  reducedMotion = false,
}: ParticleEdgeProps) {
  const meshRef = useRef<THREE.InstancedMesh>(null!);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  const curve = useMemo(() => {
    const p1 = new THREE.Vector3(...sourcePos);
    const p2 = new THREE.Vector3(...targetPos);
    const mid = new THREE.Vector3()
      .addVectors(p1, p2)
      .multiplyScalar(0.5)
      .add(new THREE.Vector3(0, 0.45, 0));
    return new THREE.QuadraticBezierCurve3(p1, mid, p2);
  }, [sourcePos, targetPos]);

  const lineGeometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints(curve.getPoints(24));
  }, [curve]);

  useFrame(({ clock }) => {
    if (!meshRef.current || !isActive || reducedMotion) return;
    const t = clock.getElapsedTime() * 0.75;
    for (let i = 0; i < particleCount; i++) {
      const phase = (t + i / particleCount) % 1;
      const pt = curve.getPoint(phase);
      dummy.position.copy(pt);
      const scale = Math.sin(phase * Math.PI) * 0.16 + 0.05;
      dummy.scale.set(scale, scale, scale);
      dummy.updateMatrix();
      meshRef.current.setMatrixAt(i, dummy.matrix);
    }
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <group>
      <primitive
        object={
          new THREE.Line(
            lineGeometry,
            new THREE.LineBasicMaterial({
              color: isActive ? color : '#1e293b',
              transparent: true,
              opacity: isActive ? 0.95 : 0.25,
            })
          )
        }
      />
      {isActive && (
        <instancedMesh ref={meshRef} args={[undefined, undefined, particleCount]}>
          <sphereGeometry args={[1, 8, 8]} />
          <meshBasicMaterial color={color} />
        </instancedMesh>
      )}
    </group>
  );
}

// -------------------------------------------------------------
// 2. Cyber Node with Dynamic Shading (idle/running/success/skipped/failed)
// -------------------------------------------------------------
function CyberNode3D({
  node,
  position,
  isSelected,
  nodeState = 'idle',
  onSelect,
  reducedMotion = false,
}: {
  node: TopologyNode;
  position: [number, number, number];
  isSelected: boolean;
  nodeState: NodeState;
  onSelect: () => void;
  reducedMotion?: boolean;
}) {
  const groupRef = useRef<THREE.Group>(null!);
  const [hovered, setHovered] = useState(false);
  const config = getAgentVisualConfig(node.id, node.type);

  // Dynamic shading by node state
  const stateColor = useMemo(() => {
    switch (nodeState) {
      case 'running':
        return '#00f0ff'; // Cyan pulsing
      case 'success':
        return '#10b981'; // Emerald success
      case 'skipped':
        return '#64748b'; // Slate skipped
      case 'failed':
        return '#ef4444'; // Red failure
      case 'idle':
      default:
        return config.color;
    }
  }, [nodeState, config.color]);

  useFrame(({ clock }) => {
    if (!groupRef.current || reducedMotion) return;
    if (nodeState === 'running') {
      const pulse = 1 + Math.sin(clock.getElapsedTime() * 7) * 0.08;
      groupRef.current.scale.set(pulse, pulse, pulse);
    } else if (hovered || isSelected) {
      groupRef.current.scale.set(1.05, 1.05, 1.05);
    } else {
      groupRef.current.scale.set(1, 1, 1);
    }
  });

  const IconComponent = config.icon;

  return (
    <group
      ref={groupRef}
      position={position}
      onClick={(e) => {
        e.stopPropagation();
        onSelect();
      }}
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
      }}
      onPointerOut={() => setHovered(false)}
    >
      {/* Base Platform */}
      <mesh position={[0, -0.15, 0]}>
        <cylinderGeometry args={[config.radius, config.radius * 1.1, 0.35, 24]} />
        <meshStandardMaterial color="#060b17" roughness={0.3} metalness={0.9} />
      </mesh>

      {/* State Glow Ring */}
      <mesh position={[0, 0.05, 0]}>
        <torusGeometry args={[config.radius, 0.05, 12, 36]} />
        <meshBasicMaterial color={stateColor} />
      </mesh>

      {/* Central Cyber Core */}
      <mesh position={[0, 0.8, 0]}>
        <octahedronGeometry args={[0.75, 0]} />
        <meshStandardMaterial
          color={stateColor}
          emissive={stateColor}
          emissiveIntensity={nodeState === 'running' ? 0.9 : 0.5}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>

      {/* HTML Overlay Label (CSP Compliant: No Troika Text) */}
      <Html position={[0, 1.85, 0]} center distanceFactor={24} zIndexRange={[100, 0]}>
        <div
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') onSelect();
          }}
          className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-950/95 border ${
            nodeState === 'failed'
              ? 'border-rose-500 shadow-[0_0_15px_rgba(239,68,68,0.5)]'
              : nodeState === 'running'
              ? 'border-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.5)]'
              : nodeState === 'success'
              ? 'border-emerald-500'
              : isSelected
              ? 'border-cyan-400 ring-2 ring-cyan-400/50'
              : 'border-slate-800'
          } shadow-xl backdrop-blur-md cursor-pointer select-none whitespace-nowrap transition-all`}
        >
          <div
            className="p-1 rounded-md"
            style={{ backgroundColor: `${stateColor}25`, color: stateColor }}
          >
            <IconComponent className="w-3.5 h-3.5" />
          </div>
          <div className="text-left font-mono">
            <div className="text-[11px] font-bold text-slate-100 flex items-center gap-1.5">
              <span>{config.label}</span>
              <span
                className={`px-1 py-0.2 rounded text-[8px] uppercase font-bold ${
                  nodeState === 'running'
                    ? 'bg-cyan-500/20 text-cyan-300'
                    : nodeState === 'success'
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : nodeState === 'skipped'
                    ? 'bg-slate-700/50 text-slate-400'
                    : nodeState === 'failed'
                    ? 'bg-rose-500/20 text-rose-300'
                    : 'bg-slate-800 text-slate-400'
                }`}
              >
                {nodeState}
              </span>
            </div>
            {(hovered || isSelected) && (
              <div className="text-[9px] text-slate-400 font-sans">{config.subtitle}</div>
            )}
          </div>
        </div>
      </Html>
    </group>
  );
}

// -------------------------------------------------------------
// 3. Domain Shift Scene: 3D PCA Point Clouds with Real CORAL Animation
// -------------------------------------------------------------
function DomainShiftScene({
  shiftData,
  reducedMotion = false,
}: {
  shiftData: ShiftPCAResponse | null;
  reducedMotion?: boolean;
}) {
  const [alignmentAlpha, setAlignmentAlpha] = useState<number>(0.0);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const meshSourceRef = useRef<THREE.InstancedMesh>(null!);
  const meshTargetRef = useRef<THREE.InstancedMesh>(null!);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  useEffect(() => {
    if (!isPlaying || reducedMotion) return;
    const interval = setInterval(() => {
      setAlignmentAlpha((prev) => {
        const next = prev + 0.015;
        return next > 1.0 ? 0.0 : next;
      });
    }, 30);
    return () => clearInterval(interval);
  }, [isPlaying, reducedMotion]);

  const sourcePoints = shiftData?.source_points || [];
  const targetPoints = shiftData?.target_points || [];
  const alignedPoints = shiftData?.aligned_points || [];

  useFrame(() => {
    if (!meshSourceRef.current || sourcePoints.length === 0) return;

    for (let i = 0; i < sourcePoints.length; i++) {
      const src = sourcePoints[i];
      const aln = alignedPoints[i] || src;

      // Real Class-Aware CORAL interpolation between original and aligned coordinates
      const x = THREE.MathUtils.lerp(src.x, aln.x, alignmentAlpha);
      const y = THREE.MathUtils.lerp(src.y, aln.y, alignmentAlpha);
      const z = THREE.MathUtils.lerp(src.z, aln.z, alignmentAlpha);

      dummy.position.set(x, y, z);
      dummy.scale.set(0.18, 0.18, 0.18);
      dummy.updateMatrix();
      meshSourceRef.current.setMatrixAt(i, dummy.matrix);
    }
    meshSourceRef.current.instanceMatrix.needsUpdate = true;
  });

  useEffect(() => {
    if (!meshTargetRef.current || targetPoints.length === 0) return;
    for (let i = 0; i < targetPoints.length; i++) {
      const tgt = targetPoints[i];
      dummy.position.set(tgt.x, tgt.y, tgt.z);
      dummy.scale.set(0.18, 0.18, 0.18);
      dummy.updateMatrix();
      meshTargetRef.current.setMatrixAt(i, dummy.matrix);
    }
    meshTargetRef.current.instanceMatrix.needsUpdate = true;
  }, [targetPoints, dummy]);

  return (
    <group>
      {/* 3D Coordinate Reference Axes & Floor */}
      <gridHelper args={[20, 20, '#0284c7', '#0f172a']} position={[0, -2, 0]} />

      {/* Source Point Cloud (CICIoT) */}
      {sourcePoints.length > 0 && (
        <instancedMesh
          ref={meshSourceRef}
          args={[undefined, undefined, sourcePoints.length]}
        >
          <sphereGeometry args={[1, 12, 12]} />
          <meshStandardMaterial
            color="#38bdf8"
            emissive="#0284c7"
            emissiveIntensity={0.6}
            metalness={0.7}
          />
        </instancedMesh>
      )}

      {/* Target Point Cloud (NF-ToN) */}
      {targetPoints.length > 0 && (
        <instancedMesh
          ref={meshTargetRef}
          args={[undefined, undefined, targetPoints.length]}
        >
          <sphereGeometry args={[1, 12, 12]} />
          <meshStandardMaterial
            color="#f43f5e"
            emissive="#be123c"
            emissiveIntensity={0.6}
            metalness={0.7}
          />
        </instancedMesh>
      )}

      {/* 3D Scene Controls & Metrics Overlay */}
      <Html position={[0, 4.2, 0]} center distanceFactor={20} zIndexRange={[100, 0]}>
        <div className="bg-slate-950/95 border border-slate-800 rounded-xl p-4 shadow-2xl backdrop-blur-md min-w-[340px] text-left font-mono">
          <div className="flex items-center justify-between gap-4 mb-3">
            <div>
              <div className="text-xs font-bold text-slate-100 uppercase tracking-wider">
                Class-Aware CORAL 3D PCA
              </div>
              <div className="text-[10px] text-slate-400">
                Source: CICIoT (Cyan) vs Target: NF-ToN (Rose)
              </div>
            </div>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="px-2 py-1 rounded bg-slate-900 border border-slate-700 text-cyan-400 text-xs hover:bg-slate-800 flex items-center gap-1"
            >
              {isPlaying ? <RotateCcw className="w-3 h-3" /> : <Play className="w-3 h-3" />}
              <span>{isPlaying ? 'Pause' : 'Play'}</span>
            </button>
          </div>

          <div className="space-y-2 mb-3">
            <div className="flex justify-between text-[11px] text-slate-300">
              <span>Alignment Progress:</span>
              <span className="text-cyan-400 font-bold">{Math.round(alignmentAlpha * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={alignmentAlpha}
              onChange={(e) => {
                setIsPlaying(false);
                setAlignmentAlpha(parseFloat(e.target.value));
              }}
              className="w-full accent-cyan-400 bg-slate-800 h-1.5 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {shiftData && (
            <div className="grid grid-cols-2 gap-2 text-[10px] border-t border-slate-800 pt-2">
              <div className="bg-slate-900/60 p-2 rounded">
                <div className="text-slate-400">Mean KS Before:</div>
                <div className="text-rose-400 font-bold text-sm">
                  {shiftData.metrics.mean_ks_before}
                </div>
                <div className="text-slate-500 text-[9px]">Mean PSI: {shiftData.metrics.mean_psi_before}</div>
              </div>
              <div className="bg-slate-900/60 p-2 rounded">
                <div className="text-slate-400">Mean KS After:</div>
                <div className="text-emerald-400 font-bold text-sm">
                  {shiftData.metrics.mean_ks_after}
                </div>
                <div className="text-slate-500 text-[9px]">Mean PSI: {shiftData.metrics.mean_psi_after}</div>
              </div>
            </div>
          )}
        </div>
      </Html>
    </group>
  );
}

// -------------------------------------------------------------
// 4. SHAP Scene: 3D Bars for Flow Attributions
// -------------------------------------------------------------
function ShapBarsScene({
  shapValues,
  topFeature,
}: {
  shapValues: Record<string, number>;
  topFeature?: string;
}) {
  const features = [
    { key: 'pkt_mean_to_max', label: 'Pkt Mean/Max' },
    { key: 'tcp_flag_density', label: 'TCP Flag Density' },
    { key: 'log_pkt_mean', label: 'Log Pkt Mean' },
    { key: 'log_pkt_max', label: 'Log Pkt Max' },
  ];

  const totalAbs = useMemo(() => {
    return Object.values(shapValues).reduce((acc, v) => acc + Math.abs(v), 0) || 1.0;
  }, [shapValues]);

  return (
    <group position={[0, -1, 0]}>
      <gridHelper args={[16, 16, '#38bdf8', '#0f172a']} position={[0, 0, 0]} />

      {features.map((feat, idx) => {
        const val = shapValues[feat.key] ?? 0.0;
        const isTop = topFeature === feat.key;
        const isPositive = val >= 0;
        const height = Math.max(0.3, Math.abs(val) * 4.0);
        const xPos = (idx - 1.5) * 3.0;
        const barColor = isPositive ? '#f43f5e' : '#10b981';
        const impactPct = Math.round((Math.abs(val) / totalAbs) * 100);

        return (
          <group key={feat.key} position={[xPos, 0, 0]}>
            {/* Pedestal */}
            <mesh position={[0, 0.1, 0]}>
              <cylinderGeometry args={[1.0, 1.1, 0.2, 24]} />
              <meshStandardMaterial color="#0b1329" metalness={0.8} roughness={0.3} />
            </mesh>

            {/* 3D Attrib Bar */}
            <mesh position={[0, height / 2 + 0.2, 0]}>
              <boxGeometry args={[1.2, height, 1.2]} />
              <meshStandardMaterial
                color={barColor}
                emissive={barColor}
                emissiveIntensity={isTop ? 0.7 : 0.4}
                metalness={0.6}
                roughness={0.25}
              />
            </mesh>

            {/* Top impact halo */}
            {isTop && (
              <mesh position={[0, height + 0.6, 0]}>
                <torusGeometry args={[0.8, 0.05, 12, 32]} />
                <meshBasicMaterial color="#fbbf24" />
              </mesh>
            )}

            {/* Feature Label & Attribution Html Overlay */}
            <Html position={[0, height + 0.9, 0]} center distanceFactor={22} zIndexRange={[100, 0]}>
              <div
                className={`bg-slate-950/95 border ${
                  isTop ? 'border-amber-400 ring-2 ring-amber-400/30' : 'border-slate-800'
                } rounded-lg p-2 text-center font-mono shadow-xl backdrop-blur-md min-w-[130px]`}
              >
                <div className="text-[10px] font-bold text-slate-200">{feat.label}</div>
                <div
                  className={`text-xs font-extrabold ${isPositive ? 'text-rose-400' : 'text-emerald-400'}`}
                >
                  {val >= 0 ? `+${val.toFixed(4)}` : val.toFixed(4)}
                </div>
                <div className="text-[9px] text-slate-400">{impactPct}% impact</div>
              </div>
            </Html>
          </group>
        );
      })}
    </group>
  );
}

// -------------------------------------------------------------
// 5. Decision Timeline Scene: 3D Arc with Stage Cards & Approval
// -------------------------------------------------------------
function DecisionTimelineScene({
  incident,
  onApprove,
}: {
  incident: any;
  onApprove?: (id: string) => void;
}) {
  const stages = [
    { name: 'Data Intelligence', status: 'SUCCESS', icon: Database, color: '#06b6d4', desc: 'Harmonized 4 features' },
    { name: 'Threat Analysis', status: 'SUCCESS', icon: Crosshair, color: '#f43f5e', desc: 'CORAL Adapted Inference' },
    { name: 'Explainability', status: 'SUCCESS', icon: BarChart3, color: '#a855f7', desc: 'TreeSHAP Computed' },
    { name: 'Knowledge Context', status: 'SUCCESS', icon: BookOpen, color: '#3b82f6', desc: 'MITRE ATT&CK Linked' },
    { name: 'Risk Prediction', status: 'SUCCESS', icon: AlertTriangle, color: '#f59e0b', desc: `Risk: ${incident?.risk_score ?? 68}/100` },
    { name: 'Decision Support', status: 'SUCCESS', icon: ShieldCheck, color: '#10b981', desc: 'Playbook Formulated' },
  ];

  const approvalReq = incident?.approval_required ?? false;
  const approvalStatus = incident?.approval_status ?? 'PENDING';

  return (
    <group position={[0, -0.5, 0]}>
      <gridHelper args={[24, 24, '#0ea5e9', '#091e3a']} position={[0, -0.2, 0]} />

      {stages.map((stage, idx) => {
        const angle = (idx / (stages.length - 1)) * Math.PI - Math.PI / 2;
        const radius = 8.5;
        const x = Math.sin(angle) * radius;
        const z = -Math.cos(angle) * radius * 0.45;
        const Icon = stage.icon;

        return (
          <group key={stage.name} position={[x, 0.4, z]}>
            {/* Pedestal */}
            <mesh position={[0, -0.2, 0]}>
              <cylinderGeometry args={[0.9, 1.0, 0.3, 24]} />
              <meshStandardMaterial color="#0b1329" metalness={0.8} roughness={0.3} />
            </mesh>

            {/* Glowing Pillar */}
            <mesh position={[0, 0.6, 0]}>
              <cylinderGeometry args={[0.3, 0.3, 1.2, 16]} />
              <meshStandardMaterial
                color={stage.color}
                emissive={stage.color}
                emissiveIntensity={0.6}
              />
            </mesh>

            {/* HTML Stage Card */}
            <Html position={[0, 1.8, 0]} center distanceFactor={22} zIndexRange={[100, 0]}>
              <div className="bg-slate-950/95 border border-slate-800 rounded-lg p-2.5 font-mono text-left shadow-2xl backdrop-blur-md min-w-[150px]">
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-100 mb-0.5">
                  <Icon className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{stage.name}</span>
                </div>
                <div className="text-[10px] text-slate-400">{stage.desc}</div>
                <div className="text-[9px] text-emerald-400 mt-1 font-semibold flex items-center gap-1">
                  <CheckCircle className="w-2.5 h-2.5" />
                  <span>{stage.status}</span>
                </div>
              </div>
            </Html>
          </group>
        );
      })}

      {/* Central Approval Pedestal */}
      <group position={[0, 0.5, 0]}>
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[2.0, 2.2, 0.4, 32]} />
          <meshStandardMaterial color="#0f172a" metalness={0.9} roughness={0.2} />
        </mesh>
        <mesh position={[0, 0.22, 0]}>
          <torusGeometry args={[2.0, 0.05, 16, 48]} />
          <meshBasicMaterial color={approvalReq ? '#f59e0b' : '#10b981'} />
        </mesh>

        <Html position={[0, 1.5, 0]} center distanceFactor={22} zIndexRange={[100, 0]}>
          <div className="bg-slate-950/95 border border-amber-500/60 rounded-xl p-4 font-mono text-left shadow-2xl backdrop-blur-md min-w-[280px]">
            <div className="text-xs font-bold text-slate-100 mb-1 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-amber-400" />
              <span>Incident Response Approval State</span>
            </div>
            <div className="text-[11px] text-slate-300 mb-2">
              Status:{' '}
              <span
                className={`font-bold ${
                  approvalStatus === 'APPROVED' ? 'text-emerald-400' : 'text-amber-400'
                }`}
              >
                {approvalStatus}
              </span>
            </div>
            {approvalReq && approvalStatus === 'PENDING' && (
              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => onApprove && onApprove(incident?.incident_id || 'test-inc')}
                  className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs"
                >
                  Approve Mitigation
                </button>
                <button className="px-3 py-1.5 rounded bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs">
                  Reject
                </button>
              </div>
            )}
          </div>
        </Html>
      </group>
    </group>
  );
}

// -------------------------------------------------------------
// Main Topology Canvas 3D Export
// -------------------------------------------------------------
export function TopologyCanvas3D({
  nodes,
  edges,
  selectedNode,
  onSelectNode,
  activeEvents,
  layoutMode = 'architecture',
  sceneMode = 'TOPOLOGY',
  quality = 'high',
  reducedMotion = false,
  shiftData,
  selectedIncident,
  flowExplanation,
  nodeStatusMap = {},
  onApproveIncident,
}: TopologyCanvas3DProps) {
  // Circular layout for nodes
  const nodePositions = useMemo(() => {
    const map = new Map<string, [number, number, number]>();
    const radius = 8.5;
    const specialized = nodes.filter((n) => n.id !== 'orchestrator' && n.id !== 'message_bus' && n.id !== 'api_gateway');

    // Central core
    map.set('orchestrator', [0, 0.4, 0]);
    map.set('message_bus', [0, 0.4, 3.2]);
    map.set('api_gateway', [0, 0.4, -3.2]);

    specialized.forEach((n, idx) => {
      const angle = (idx / specialized.length) * Math.PI * 2;
      map.set(n.id, [Math.cos(angle) * radius, 0.4, Math.sin(angle) * radius]);
    });

    return map;
  }, [nodes]);

  // Active edges tracking
  const activeEdgeKeys = useMemo(() => {
    const set = new Set<string>();
    activeEvents.forEach((evt) => {
      set.add(`${evt.source_node}->${evt.target_node}`);
    });
    return set;
  }, [activeEvents]);

  const defaultShap = useMemo(() => {
    return flowExplanation?.shap_values || {
      pkt_mean_to_max: -0.1942,
      tcp_flag_density: 0.4281,
      log_pkt_mean: -0.0815,
      log_pkt_max: 0.3129,
    };
  }, [flowExplanation]);

  return (
    <div className="w-full h-full relative bg-slate-950">
      <Canvas
        camera={{ position: [0, 16, 22], fov: 48 }}
        dpr={quality === 'high' ? [1, 2] : 1}
        gl={{ antialias: quality === 'high', powerPreference: 'high-performance' }}
      >
        <color attach="background" args={['#030712']} />
        <ambientLight intensity={0.65} />
        <directionalLight position={[10, 20, 15]} intensity={1.2} />
        <pointLight position={[-10, 10, -10]} intensity={0.5} color="#00f0ff" />

        <Suspense fallback={null}>
          {sceneMode === 'TOPOLOGY' && (
            <group>
              <gridHelper args={[36, 36, '#0ea5e9', '#091e3a']} position={[0, -0.3, 0]} />

              {/* Edge Connections with Instanced Flow Particles */}
              {edges.map((edge) => {
                const sPos = nodePositions.get(edge.source);
                const tPos = nodePositions.get(edge.target);
                if (!sPos || !tPos) return null;
                const isActive = activeEdgeKeys.has(`${edge.source}->${edge.target}`);

                return (
                  <InstancedParticleEdge
                    key={`${edge.source}-${edge.target}`}
                    sourcePos={sPos}
                    targetPos={tPos}
                    color="#00f0ff"
                    isActive={isActive}
                    particleCount={quality === 'high' ? 14 : 6}
                    reducedMotion={reducedMotion}
                  />
                );
              })}

              {/* Agent Nodes with Real State Shading */}
              {nodes.map((node) => {
                const pos = nodePositions.get(node.id) || [0, 0, 0];
                const state = nodeStatusMap[node.id.toUpperCase()] || nodeStatusMap[node.id.toLowerCase()] || 'idle';

                return (
                  <CyberNode3D
                    key={node.id}
                    node={node}
                    position={pos}
                    isSelected={selectedNode?.id === node.id}
                    nodeState={state}
                    onSelect={() => onSelectNode(node)}
                    reducedMotion={reducedMotion}
                  />
                );
              })}
            </group>
          )}

          {sceneMode === 'DOMAIN_SHIFT' && (
            <DomainShiftScene shiftData={shiftData || null} reducedMotion={reducedMotion} />
          )}

          {sceneMode === 'SHAP' && (
            <ShapBarsScene
              shapValues={defaultShap}
              topFeature={flowExplanation?.top_feature || 'tcp_flag_density'}
            />
          )}

          {sceneMode === 'DECISION_TIMELINE' && (
            <DecisionTimelineScene
              incident={selectedIncident}
              onApprove={onApproveIncident}
            />
          )}
        </Suspense>

        <OrbitControls
          enableDamping
          dampingFactor={0.08}
          minDistance={6}
          maxDistance={50}
          maxPolarAngle={Math.PI / 2.05}
          autoRotate={!reducedMotion && sceneMode === 'TOPOLOGY'}
          autoRotateSpeed={0.35}
        />
      </Canvas>
    </div>
  );
}

export default TopologyCanvas3D;
