import React, { useRef, useMemo, useState, Suspense } from 'react';
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
  Shield,
  Activity,
} from 'lucide-react';
import { TopologyNode, TopologyEdge, FlowEventItem } from '../../api/client';

export interface TopologyCanvas3DProps {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  selectedNode: TopologyNode | null;
  onSelectNode: (node: TopologyNode) => void;
  activeEvents: FlowEventItem[];
  layoutMode?: 'architecture' | 'topology';
}

// Color palette mapping based on role and cyber identity
function getAgentVisualConfig(nodeId: string, nodeType: string) {
  switch (nodeId.toLowerCase()) {
    case 'orchestrator':
      return {
        color: '#00f0ff',
        accent: '#818cf8',
        icon: Workflow,
        label: 'ARGUS Orchestrator',
        subtitle: 'Central Cognitive Core & Workflow Engine',
        radius: 2.2,
      };
    case 'data_intelligence':
      return {
        color: '#06b6d4',
        accent: '#38bdf8',
        icon: Database,
        label: 'Data Intelligence Agent',
        subtitle: 'Telemetry Ingestion & Harmonization',
        radius: 1.5,
      };
    case 'threat_analysis':
      return {
        color: '#f43f5e',
        accent: '#fb7185',
        icon: Crosshair,
        label: 'Threat Analysis Agent',
        subtitle: 'CORAL D1->D2 ML Inference',
        radius: 1.5,
      };
    case 'explainability':
      return {
        color: '#a855f7',
        accent: '#c084fc',
        icon: BarChart3,
        label: 'Explainability Agent',
        subtitle: 'TreeSHAP Feature Attributions',
        radius: 1.5,
      };
    case 'knowledge_context':
      return {
        color: '#3b82f6',
        accent: '#60a5fa',
        icon: BookOpen,
        label: 'Knowledge Context Agent',
        subtitle: 'MITRE ATT&CK for ICS Matrix',
        radius: 1.5,
      };
    case 'risk_prediction':
      return {
        color: '#f59e0b',
        accent: '#fbbf24',
        icon: AlertTriangle,
        label: 'Risk Prediction Agent',
        subtitle: 'Operational Grid Impact & Criticality',
        radius: 1.5,
      };
    case 'decision_support':
      return {
        color: '#10b981',
        accent: '#34d399',
        icon: ShieldCheck,
        label: 'Decision Support Agent',
        subtitle: 'Automated Containment Playbooks',
        radius: 1.5,
      };
    case 'api_gateway':
      return {
        color: '#38bdf8',
        accent: '#7dd3fc',
        icon: Radio,
        label: 'API Gateway',
        subtitle: 'Flow Ingress & Telemetry Termination',
        radius: 1.35,
      };
    case 'message_bus':
      return {
        color: '#00f0ff',
        accent: '#67e8f9',
        icon: Zap,
        label: 'Event Message Bus',
        subtitle: 'Asynchronous Pub/Sub Telemetry Broker',
        radius: 1.35,
      };
    case 'policy_engine':
      return {
        color: '#6366f1',
        accent: '#a5b4fc',
        icon: Lock,
        label: 'Policy Engine',
        subtitle: 'Deterministic Mitigation Verification',
        radius: 1.35,
      };
    default:
      return {
        color: nodeType === 'engine' ? '#8b5cf6' : nodeType === 'bus' ? '#06b6d4' : '#3b82f6',
        accent: '#38bdf8',
        icon: Cpu,
        label: nodeId,
        subtitle: 'Cyber System Component',
        radius: 1.4,
      };
  }
}

// 3D Geometry specific to each node's cyber role
function NodeGeometry({ nodeId }: { nodeId: string }) {
  const meshRef = useRef<THREE.Mesh>(null!);
  const ringRef = useRef<THREE.Mesh>(null!);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (meshRef.current) {
      if (nodeId === 'orchestrator') {
        meshRef.current.rotation.y = t * 0.4;
        meshRef.current.rotation.x = Math.sin(t * 0.3) * 0.15;
      } else {
        meshRef.current.rotation.y = t * 0.2;
      }
    }
    if (ringRef.current) {
      ringRef.current.rotation.z = -t * 0.6;
    }
  });

  const id = nodeId.toLowerCase();

  if (id === 'orchestrator') {
    return (
      <group position={[0, 0.9, 0]}>
        {/* Outer rotating cyber-lattice cage */}
        <mesh ref={meshRef}>
          <dodecahedronGeometry args={[1.15, 0]} />
          <meshStandardMaterial
            color="#00f0ff"
            emissive="#00f0ff"
            emissiveIntensity={0.4}
            wireframe
            transparent
            opacity={0.7}
          />
        </mesh>
        {/* Inner pulsing power core */}
        <mesh>
          <octahedronGeometry args={[0.7, 0]} />
          <meshStandardMaterial
            color="#38bdf8"
            emissive="#0284c7"
            emissiveIntensity={0.8}
            roughness={0.1}
            metalness={0.9}
          />
        </mesh>
        {/* Rotating horizontal orbital ring */}
        <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[1.5, 0.03, 16, 64]} />
          <meshBasicMaterial color="#00f0ff" transparent opacity={0.8} />
        </mesh>
      </group>
    );
  }

  if (id === 'data_intelligence') {
    return (
      <group position={[0, 0.7, 0]}>
        {/* Stacked data disks */}
        <mesh position={[0, -0.3, 0]}>
          <cylinderGeometry args={[0.65, 0.65, 0.2, 24]} />
          <meshStandardMaterial color="#0e7490" emissive="#06b6d4" emissiveIntensity={0.5} metalness={0.8} />
        </mesh>
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[0.65, 0.65, 0.2, 24]} />
          <meshStandardMaterial color="#0e7490" emissive="#06b6d4" emissiveIntensity={0.6} metalness={0.8} />
        </mesh>
        <mesh position={[0, 0.3, 0]}>
          <cylinderGeometry args={[0.65, 0.65, 0.2, 24]} />
          <meshStandardMaterial color="#0e7490" emissive="#06b6d4" emissiveIntensity={0.7} metalness={0.8} />
        </mesh>
      </group>
    );
  }

  if (id === 'threat_analysis') {
    return (
      <group position={[0, 0.8, 0]}>
        {/* Threat Detection Crystal Octahedron */}
        <mesh ref={meshRef}>
          <octahedronGeometry args={[0.8, 0]} />
          <meshStandardMaterial
            color="#f43f5e"
            emissive="#e11d48"
            emissiveIntensity={0.7}
            roughness={0.15}
            metalness={0.85}
          />
        </mesh>
      </group>
    );
  }

  if (id === 'explainability') {
    return (
      <group position={[0, 0.8, 0]}>
        {/* SHAP Prism Icosahedron */}
        <mesh ref={meshRef}>
          <icosahedronGeometry args={[0.75, 0]} />
          <meshStandardMaterial
            color="#a855f7"
            emissive="#9333ea"
            emissiveIntensity={0.6}
            roughness={0.2}
            metalness={0.8}
          />
        </mesh>
      </group>
    );
  }

  if (id === 'knowledge_context') {
    return (
      <group position={[0, 0.8, 0]}>
        {/* MITRE Knowledge Cube */}
        <mesh ref={meshRef}>
          <boxGeometry args={[0.9, 0.9, 0.9]} />
          <meshStandardMaterial
            color="#2563eb"
            emissive="#1d4ed8"
            emissiveIntensity={0.6}
            roughness={0.2}
            metalness={0.85}
          />
        </mesh>
      </group>
    );
  }

  if (id === 'risk_prediction') {
    return (
      <group position={[0, 0.8, 0]}>
        {/* Risk Assessment Conical Beacon */}
        <mesh ref={meshRef}>
          <coneGeometry args={[0.7, 1.2, 16]} />
          <meshStandardMaterial
            color="#f59e0b"
            emissive="#d97706"
            emissiveIntensity={0.65}
            roughness={0.2}
            metalness={0.8}
          />
        </mesh>
      </group>
    );
  }

  if (id === 'decision_support') {
    return (
      <group position={[0, 0.8, 0]}>
        {/* Mitigation Shield Prism */}
        <mesh ref={meshRef}>
          <cylinderGeometry args={[0.7, 0.7, 0.8, 6]} />
          <meshStandardMaterial
            color="#10b981"
            emissive="#059669"
            emissiveIntensity={0.6}
            roughness={0.2}
            metalness={0.8}
          />
        </mesh>
      </group>
    );
  }

  if (id === 'api_gateway') {
    return (
      <group position={[0, 0.7, 0]}>
        {/* Ingress Gateway Sensor Sphere & Ring */}
        <mesh>
          <sphereGeometry args={[0.65, 24, 24]} />
          <meshStandardMaterial color="#38bdf8" emissive="#0284c7" emissiveIntensity={0.5} />
        </mesh>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.9, 0.03, 16, 32]} />
          <meshBasicMaterial color="#38bdf8" />
        </mesh>
      </group>
    );
  }

  if (id === 'message_bus') {
    return (
      <group position={[0, 0.7, 0]}>
        {/* Dual Bus Conduits */}
        <mesh position={[-0.25, 0, 0]}>
          <cylinderGeometry args={[0.25, 0.25, 0.9, 16]} />
          <meshStandardMaterial color="#00f0ff" emissive="#0891b2" emissiveIntensity={0.7} />
        </mesh>
        <mesh position={[0.25, 0, 0]}>
          <cylinderGeometry args={[0.25, 0.25, 0.9, 16]} />
          <meshStandardMaterial color="#00f0ff" emissive="#0891b2" emissiveIntensity={0.7} />
        </mesh>
      </group>
    );
  }

  // Fallback for policy_engine / other nodes
  return (
    <group position={[0, 0.75, 0]}>
      <mesh ref={meshRef}>
        <octahedronGeometry args={[0.7, 0]} />
        <meshStandardMaterial color="#6366f1" emissive="#4f46e5" emissiveIntensity={0.6} />
      </mesh>
    </group>
  );
}

interface CyberPlatformProps {
  node: TopologyNode;
  position: [number, number, number];
  isSelected: boolean;
  onSelect: (node: TopologyNode) => void;
}

function CyberPlatform({ node, position, isSelected, onSelect }: CyberPlatformProps) {
  const [hovered, setHovered] = useState(false);
  const platformRef = useRef<THREE.Group>(null!);
  const config = getAgentVisualConfig(node.id, node.type);
  const IconComponent = config.icon;

  // Pulse effect if active / busy
  useFrame(({ clock }) => {
    if (platformRef.current && (node.status === 'busy' || hovered)) {
      const scale = 1 + Math.sin(clock.getElapsedTime() * 4) * 0.04;
      platformRef.current.scale.set(scale, scale, scale);
    }
  });

  const statusBorderColor =
    node.status === 'busy'
      ? 'border-emerald-400 text-emerald-300'
      : node.status === 'failed'
      ? 'border-rose-500 text-rose-300'
      : node.status === 'blocked'
      ? 'border-amber-400 text-amber-300'
      : 'border-cyan-500/50 text-cyan-200';

  return (
    <group
      ref={platformRef}
      position={position}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(node);
      }}
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
      }}
      onPointerOut={() => setHovered(false)}
    >
      {/* Selection Holographic Beacon */}
      {isSelected && (
        <group>
          <mesh position={[0, 1.2, 0]}>
            <cylinderGeometry args={[config.radius * 1.25, config.radius * 1.25, 3.0, 32, 1, true]} />
            <meshBasicMaterial color="#00f0ff" transparent opacity={0.15} side={THREE.DoubleSide} />
          </mesh>
          <mesh position={[0, 2.7, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[config.radius * 1.15, config.radius * 1.25, 32]} />
            <meshBasicMaterial color="#00f0ff" />
          </mesh>
        </group>
      )}

      {/* Cyber Platform Base Cylinder */}
      <mesh position={[0, -0.15, 0]}>
        <cylinderGeometry args={[config.radius, config.radius * 1.1, 0.35, 32]} />
        <meshStandardMaterial
          color="#060b17"
          roughness={0.25}
          metalness={0.92}
        />
      </mesh>

      {/* Glowing Outer Edge Ring */}
      <mesh position={[0, 0.02, 0]}>
        <torusGeometry args={[config.radius, 0.035, 16, 48]} />
        <meshBasicMaterial color={config.color} />
      </mesh>

      {/* Floor Projection Hologram Ring */}
      <mesh position={[0, -0.32, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[config.radius * 1.15, config.radius * 1.35, 48]} />
        <meshBasicMaterial color={config.color} transparent opacity={hovered || isSelected ? 0.6 : 0.25} />
      </mesh>

      {/* The Central Role-Specific 3D Geometry */}
      <NodeGeometry nodeId={node.id} />

      {/* Crisp HTML Label and Cyber Badge */}
      <Html position={[0, 1.8, 0]} center distanceFactor={22} zIndexRange={[100, 0]}>
        <div
          className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-950/90 border ${statusBorderColor} shadow-xl backdrop-blur-md cursor-pointer transition-all duration-200 select-none whitespace-nowrap hover:scale-105`}
        >
          <div
            className="p-1 rounded-md"
            style={{ backgroundColor: `${config.color}20`, color: config.color }}
          >
            <IconComponent className="w-3.5 h-3.5" />
          </div>

          <div className="text-left font-mono">
            <div className="text-[11px] font-bold text-slate-100 flex items-center gap-1.5">
              <span>{config.label}</span>
              {node.implementation_type === 'stub' && (
                <span className="px-1 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[8px] border border-amber-500/40">
                  STUB
                </span>
              )}
            </div>
            {(hovered || isSelected) && (
              <div className="text-[9px] text-slate-400 font-sans max-w-[200px] truncate">
                {config.subtitle}
              </div>
            )}
          </div>
        </div>
      </Html>
    </group>
  );
}

// Particle traveling along active connection paths
function FlowParticle({ startPos, endPos, speed = 1.8 }: { startPos: [number, number, number]; endPos: [number, number, number]; speed?: number }) {
  const meshRef = useRef<THREE.Mesh>(null!);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      const progress = (clock.getElapsedTime() * speed) % 1;
      meshRef.current.position.set(
        THREE.MathUtils.lerp(startPos[0], endPos[0], progress),
        THREE.MathUtils.lerp(startPos[1] + 0.3, endPos[1] + 0.3, progress),
        THREE.MathUtils.lerp(startPos[2], endPos[2], progress)
      );
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.22, 16, 16]} />
      <meshBasicMaterial color="#00f0ff" />
    </mesh>
  );
}

interface CyberConnectionProps {
  sourcePos: [number, number, number];
  targetPos: [number, number, number];
  isActive: boolean;
  color?: string;
}

function CyberConnection({ sourcePos, targetPos, isActive, color = '#00f0ff' }: CyberConnectionProps) {
  const points = useMemo(() => {
    const p1 = new THREE.Vector3(...sourcePos);
    const p2 = new THREE.Vector3(...targetPos);
    // Slight upward arc for cyber conduit feel
    const mid = new THREE.Vector3()
      .addVectors(p1, p2)
      .multiplyScalar(0.5)
      .add(new THREE.Vector3(0, 0.4, 0));
    return new THREE.QuadraticBezierCurve3(p1, mid, p2).getPoints(30);
  }, [sourcePos, targetPos]);

  const lineGeometry = useMemo(() => new THREE.BufferGeometry().setFromPoints(points), [points]);

  return (
    <group>
      <primitive
        object={
          new THREE.Line(
            lineGeometry,
            new THREE.LineBasicMaterial({
              color: isActive ? color : '#1e293b',
              linewidth: isActive ? 2.5 : 1,
              transparent: true,
              opacity: isActive ? 0.95 : 0.35,
            })
          )
        }
      />
      {isActive && (
        <>
          <FlowParticle startPos={sourcePos} endPos={targetPos} speed={1.6} />
          <FlowParticle startPos={sourcePos} endPos={targetPos} speed={2.4} />
        </>
      )}
    </group>
  );
}

// Floor technical grid and orbital radar rings
function CyberEnvironment() {
  return (
    <group position={[0, -0.38, 0]}>
      {/* Dark Technical Cyber Grid */}
      <gridHelper args={[40, 40, '#0ea5e9', '#091e3a']} />

      {/* Orbital Ring 1: Specialized Agents Ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[8.45, 8.55, 64]} />
        <meshBasicMaterial color="#00f0ff" transparent opacity={0.28} />
      </mesh>

      {/* Orbital Ring 2: Outer Infrastructure Ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[13.9, 14.05, 64]} />
        <meshBasicMaterial color="#3b82f6" transparent opacity={0.18} />
      </mesh>

      {/* Concentric Center Radar Rings */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[3.2, 3.25, 48]} />
        <meshBasicMaterial color="#38bdf8" transparent opacity={0.2} />
      </mesh>
    </group>
  );
}

export function TopologyCanvas3D({
  nodes,
  edges,
  selectedNode,
  onSelectNode,
  activeEvents,
  layoutMode = 'architecture',
}: TopologyCanvas3DProps) {
  // Compute positions based on selected mode
  const nodePositions = useMemo(() => {
    const posMap: Record<string, [number, number, number]> = {};

    if (layoutMode === 'architecture') {
      // 1. ARGUS Orchestrator in center
      posMap['orchestrator'] = [0, 0.4, 0];

      // 2. The 6 specialized agents in an orbital ring (Radius 8.5)
      const agentIds = [
        'data_intelligence',
        'threat_analysis',
        'explainability',
        'knowledge_context',
        'risk_prediction',
        'decision_support',
      ];
      const R_agents = 8.5;
      agentIds.forEach((id, idx) => {
        // Arrange sequentially starting at angle 0
        const angle = (idx / agentIds.length) * Math.PI * 2;
        posMap[id] = [Math.cos(angle) * R_agents, 0.1, Math.sin(angle) * R_agents];
      });

      // 3. Infrastructure components on outer perimeter
      posMap['api_gateway'] = [-13.5, 0.0, 3.5];
      posMap['message_bus'] = [-6.8, 0.1, 1.8];
      posMap['policy_engine'] = [13.5, 0.0, -3.5];

      // Any remaining nodes
      nodes.forEach((n) => {
        if (!posMap[n.id]) {
          posMap[n.id] = [12, 0, 10];
        }
      });
    } else {
      // System Topology Flow Mode: Left-to-Right Pipeline
      posMap['api_gateway'] = [-14.5, 0.0, 0];
      posMap['message_bus'] = [-9.5, 0.1, 0];
      posMap['orchestrator'] = [-4.0, 0.4, 0];

      // Specialized Agents staged column
      posMap['data_intelligence'] = [1.5, 0.1, -4.5];
      posMap['threat_analysis'] = [2.5, 0.1, 3.5];
      posMap['explainability'] = [6.0, 0.1, 3.5];
      posMap['knowledge_context'] = [5.5, 0.1, -4.5];
      posMap['risk_prediction'] = [9.5, 0.1, -2.5];
      posMap['decision_support'] = [10.5, 0.1, 2.5];

      // Monitoring / Policy Engine
      posMap['policy_engine'] = [15.0, 0.0, 0];

      nodes.forEach((n) => {
        if (!posMap[n.id]) {
          posMap[n.id] = [12, 0, 8];
        }
      });
    }

    return posMap;
  }, [nodes, layoutMode]);

  // Set of active edges from recent flow events
  const activeEdgeKeys = useMemo(() => {
    const set = new Set<string>();
    activeEvents.forEach((evt) => {
      set.add(`${evt.source_node}->${evt.target_node}`);
    });
    return set;
  }, [activeEvents]);

  // Radial orchestrator-to-agent communication links (for Architecture mode)
  const orchestratorAgentLinks = useMemo(() => {
    if (layoutMode !== 'architecture') return [];
    return [
      'data_intelligence',
      'threat_analysis',
      'explainability',
      'knowledge_context',
      'risk_prediction',
      'decision_support',
    ];
  }, [layoutMode]);

  return (
    <Canvas
      camera={{ position: [0, 16, 22], fov: 46 }}
      style={{ background: '#020617' }}
      onPointerDown={() => onSelectNode(null as any)}
    >
      {/* Cyber Lighting Environment */}
      <ambientLight intensity={0.8} color="#38bdf8" />
      <directionalLight position={[15, 25, 15]} intensity={1.5} color="#e0f2fe" />
      <pointLight position={[-15, -10, -15]} intensity={0.6} color="#818cf8" />
      <pointLight position={[0, 5, 0]} intensity={1.8} distance={16} color="#00f0ff" />

      {/* OrbitControls with smooth damping */}
      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        enableDamping
        dampingFactor={0.05}
        maxPolarAngle={Math.PI / 2.05}
        minDistance={8}
        maxDistance={42}
      />

      <Suspense fallback={null}>
        {/* Floor Cyber Grid & Radar Rings */}
        <CyberEnvironment />

        {/* Orchestrator Radial Control Beams (in Architecture mode) */}
        {orchestratorAgentLinks.map((agentId) => {
          const orchPos = nodePositions['orchestrator'] || [0, 0, 0];
          const agentPos = nodePositions[agentId];
          if (!agentPos) return null;
          const isActive = activeEvents.some(
            (e) => e.target_node === agentId || e.source_node === agentId
          );

          return (
            <CyberConnection
              key={`orch->${agentId}`}
              sourcePos={orchPos}
              targetPos={agentPos}
              isActive={isActive}
              color="#00f0ff"
            />
          );
        })}

        {/* Sequential Telemetry & Pipeline Edges */}
        {edges.map((edge) => {
          const srcPos = nodePositions[edge.source];
          const tgtPos = nodePositions[edge.target];
          if (!srcPos || !tgtPos) return null;
          const isActive = activeEdgeKeys.has(`${edge.source}->${edge.target}`);

          return (
            <CyberConnection
              key={`${edge.source}->${edge.target}`}
              sourcePos={srcPos}
              targetPos={tgtPos}
              isActive={isActive}
              color={isActive ? '#10b981' : '#00f0ff'}
            />
          );
        })}

        {/* Elevated Cyber Platforms & Agent Visuals */}
        {nodes.map((node) => {
          const pos = nodePositions[node.id] || [0, 0, 0];
          const isSelected = selectedNode?.id === node.id;

          return (
            <CyberPlatform
              key={node.id}
              node={node}
              position={pos}
              isSelected={isSelected}
              onSelect={onSelectNode}
            />
          );
        })}
      </Suspense>
    </Canvas>
  );
}
