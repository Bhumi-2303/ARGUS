import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { NetworkNode, NodeStatus, NodeType } from '../../types';

interface Node3DProps {
  node: NetworkNode;
  isSelected: boolean;
  onSelect: (node: NetworkNode) => void;
  reducedMotion: boolean;
}

// Color & Emissive mappings based on NodeStatus
export const STATUS_COLORS: Record<NodeStatus, { color: string; emissive: string; glowClass: string; borderClass: string; bgClass: string }> = {
  secure: {
    color: '#22d3ee', // Cyan
    emissive: '#0891b2',
    glowClass: 'glow-info',
    borderClass: 'border-info/40 text-info',
    bgClass: 'bg-info/10'
  },
  protected: {
    color: '#22c55e', // Green
    emissive: '#15803d',
    glowClass: 'glow-safe',
    borderClass: 'border-safe/40 text-safe',
    bgClass: 'bg-safe/10'
  },
  'at-risk': {
    color: '#eab308', // Gold
    emissive: '#a16207',
    glowClass: 'glow-warn',
    borderClass: 'border-warn/40 text-warn',
    bgClass: 'bg-warn/10'
  },
  compromised: {
    color: '#ef4444', // Red
    emissive: '#b91c1c',
    glowClass: 'glow-critical',
    borderClass: 'border-critical/40 text-critical',
    bgClass: 'bg-critical/10'
  }
};

/**
 * Geometric shape per NodeType
 */
const NodeGeometry: React.FC<{ type: NodeType; mainColor: string; emissiveColor: string }> = ({
  type,
  mainColor,
  emissiveColor
}) => {
  switch (type) {
    case 'control-center':
    case 'scada':
      return (
        <group>
          {/* Main server tower block */}
          <mesh position={[0, 0.5, 0]}>
            <boxGeometry args={[0.9, 1.0, 0.9]} />
            <meshStandardMaterial color={mainColor} emissive={emissiveColor} emissiveIntensity={0.6} metalness={0.5} roughness={0.2} />
          </mesh>
          {/* Top antenna mast */}
          <mesh position={[0, 1.2, 0]}>
            <cylinderGeometry args={[0.05, 0.05, 0.5, 8]} />
            <meshStandardMaterial color="#ffffff" emissive={mainColor} emissiveIntensity={0.8} />
          </mesh>
          {/* Glowing indicator ring */}
          <mesh position={[0, 0.6, 0]}>
            <boxGeometry args={[0.95, 0.1, 0.95]} />
            <meshBasicMaterial color={mainColor} />
          </mesh>
        </group>
      );

    case 'substation':
      return (
        <group>
          {/* Base structure */}
          <mesh position={[0, 0.2, 0]}>
            <cylinderGeometry args={[0.6, 0.7, 0.4, 6]} />
            <meshStandardMaterial color={mainColor} emissive={emissiveColor} emissiveIntensity={0.5} />
          </mesh>
          {/* Pylon / Transformer mast */}
          <mesh position={[0, 0.75, 0]}>
            <boxGeometry args={[0.4, 0.7, 0.4]} />
            <meshStandardMaterial color={mainColor} emissive={emissiveColor} emissiveIntensity={0.7} metalness={0.6} />
          </mesh>
          {/* Top insulator crossbar */}
          <mesh position={[0, 1.1, 0]}>
            <boxGeometry args={[0.9, 0.1, 0.2]} />
            <meshStandardMaterial color="#cbd5e1" emissive={mainColor} emissiveIntensity={0.4} />
          </mesh>
        </group>
      );

    case 'hmi':
      return (
        <group>
          {/* Stand */}
          <mesh position={[0, 0.2, 0]}>
            <cylinderGeometry args={[0.15, 0.25, 0.4, 8]} />
            <meshStandardMaterial color="#475569" />
          </mesh>
          {/* Angled Display Screen Panel */}
          <mesh position={[0, 0.55, 0]} rotation={[0.2, 0, 0]}>
            <boxGeometry args={[0.8, 0.55, 0.1]} />
            <meshStandardMaterial color={mainColor} emissive={emissiveColor} emissiveIntensity={0.7} metalness={0.3} roughness={0.3} />
          </mesh>
        </group>
      );

    case 'iot-sensor':
      return (
        <group>
          {/* Base ring */}
          <mesh position={[0, 0.1, 0]}>
            <cylinderGeometry args={[0.3, 0.35, 0.2, 12]} />
            <meshStandardMaterial color="#334155" />
          </mesh>
          {/* Floating Orb Sphere */}
          <mesh position={[0, 0.45, 0]}>
            <sphereGeometry args={[0.3, 16, 16]} />
            <meshStandardMaterial color={mainColor} emissive={emissiveColor} emissiveIntensity={0.9} roughness={0.1} />
          </mesh>
        </group>
      );

    case 'field-device':
      return (
        <group>
          {/* Vertical turbine mast */}
          <mesh position={[0, 0.5, 0]}>
            <cylinderGeometry args={[0.1, 0.15, 1.0, 8]} />
            <meshStandardMaterial color={mainColor} emissive={emissiveColor} emissiveIntensity={0.5} />
          </mesh>
          {/* Rotor head */}
          <mesh position={[0, 1.05, 0]}>
            <sphereGeometry args={[0.2, 12, 12]} />
            <meshStandardMaterial color="#ffffff" emissive={mainColor} emissiveIntensity={0.8} />
          </mesh>
        </group>
      );

    case 'rtu':
    case 'ied':
    case 'plc':
    default:
      return (
        <group>
          {/* Compact module cube */}
          <mesh position={[0, 0.35, 0]}>
            <boxGeometry args={[0.6, 0.6, 0.6]} />
            <meshStandardMaterial color={mainColor} emissive={emissiveColor} emissiveIntensity={0.6} metalness={0.4} roughness={0.3} />
          </mesh>
          {/* Small status LED */}
          <mesh position={[0, 0.7, 0]}>
            <sphereGeometry args={[0.08, 8, 8]} />
            <meshBasicMaterial color={mainColor} />
          </mesh>
        </group>
      );
  }
};

export const Node3DModel: React.FC<Node3DProps> = ({
  node,
  isSelected,
  onSelect,
  reducedMotion
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const platformRef = useRef<THREE.Mesh>(null);
  const breachPulseRef = useRef<THREE.Mesh>(null);

  const statusStyle = STATUS_COLORS[node.status] || STATUS_COLORS.secure;

  // Gentle idle animation & pulsing breach indicator
  useFrame((state) => {
    if (reducedMotion) return;

    const t = state.clock.getElapsedTime();

    // Subtle platform rotation
    if (platformRef.current) {
      platformRef.current.rotation.y = t * 0.2;
    }

    // Floating breathing motion
    if (groupRef.current) {
      groupRef.current.position.y = node.position.y + Math.sin(t * 1.5 + node.position.x) * 0.05;
    }

    // Breach pulse for compromised nodes
    if (node.status === 'compromised' && breachPulseRef.current) {
      const scale = 1.0 + (Math.sin(t * 4) + 1) * 0.3;
      breachPulseRef.current.scale.set(scale, scale, scale);
      const mat = breachPulseRef.current.material as THREE.MeshBasicMaterial;
      if (mat) {
        mat.opacity = 0.6 - (scale - 1.0) * 0.5;
      }
    }
  });

  return (
    <group
      position={[node.position.x, node.position.y, node.position.z]}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(node);
      }}
      onPointerOver={(e) => {
        e.stopPropagation();
        document.body.style.cursor = 'pointer';
      }}
      onPointerOut={() => {
        document.body.style.cursor = 'auto';
      }}
    >
      <group ref={groupRef}>
        {/* Selection Ring Highlight */}
        {isSelected && (
          <mesh position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[0.8, 0.95, 32]} />
            <meshBasicMaterial color="#22d3ee" side={THREE.DoubleSide} />
          </mesh>
        )}

        {/* Translucent Hexagonal Base Platform */}
        <mesh ref={platformRef} position={[0, 0.01, 0]}>
          <cylinderGeometry args={[0.75, 0.8, 0.08, 6]} />
          <meshStandardMaterial
            color={statusStyle.color}
            emissive={statusStyle.emissive}
            emissiveIntensity={0.4}
            transparent
            opacity={0.35}
            roughness={0.2}
          />
        </mesh>

        {/* Node 3D Shape */}
        <NodeGeometry type={node.type} mainColor={statusStyle.color} emissiveColor={statusStyle.emissive} />

        {/* Compromised Breach Indicator Pulse */}
        {node.status === 'compromised' && (
          <mesh ref={breachPulseRef} position={[0, 0.5, 0]}>
            <sphereGeometry args={[0.7, 16, 16]} />
            <meshBasicMaterial color="#ef4444" transparent opacity={0.3} wireframe />
          </mesh>
        )}

        {/* Floating HTML Label above Node */}
        <Html
          distanceFactor={18}
          center
          position={[0, 1.6, 0]}
          style={{ pointerEvents: 'none' }}
        >
          <div
            className={`flex flex-col items-center px-2 py-1 rounded-md bg-bg-surface-raised/90 border backdrop-blur-md transition-all ${
              isSelected
                ? 'border-info text-info ring-2 ring-info/50 scale-110'
                : `${statusStyle.borderClass} ${statusStyle.glowClass}`
            }`}
          >
            <span className="text-[10px] font-bold tracking-wider uppercase whitespace-nowrap text-text-primary">
              {node.name}
            </span>
            <div className="flex items-center gap-1 mt-0.5">
              <span className={`w-1.5 h-1.5 rounded-full ${statusStyle.bgClass}`} style={{ backgroundColor: statusStyle.color }} />
              <span className="text-[9px] font-mono tracking-widest uppercase opacity-80" style={{ color: statusStyle.color }}>
                {node.status}
              </span>
            </div>
          </div>
        </Html>
      </group>
    </group>
  );
};

export default Node3DModel;
