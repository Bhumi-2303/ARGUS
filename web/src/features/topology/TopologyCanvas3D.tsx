import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Html } from '@react-three/drei';
import * as THREE from 'three';
import { TopologyNode, TopologyEdge, FlowEventItem } from '../../api/client';

interface Node3DProps {
  node: TopologyNode;
  position: [number, number, number];
  isSelected: boolean;
  onSelect: (node: TopologyNode) => void;
}

function NodeMesh({ node, position, isSelected, onSelect }: Node3DProps) {
  const meshRef = useRef<THREE.Mesh>(null!);

  const statusColor = useMemo(() => {
    switch (node.status) {
      case 'busy':
        return '#10b981'; // emerald
      case 'blocked':
        return '#f59e0b'; // amber
      case 'failed':
        return '#f43f5e'; // rose
      default:
        return node.type === 'bus' ? '#06b6d4' : node.type === 'engine' ? '#8b5cf6' : '#3b82f6';
    }
  }, [node.status, node.type]);

  // Pulse animation for busy nodes
  useFrame(({ clock }) => {
    if (meshRef.current && node.status === 'busy') {
      const scale = 1 + Math.sin(clock.getElapsedTime() * 6) * 0.15;
      meshRef.current.scale.set(scale, scale, scale);
    }
  });

  return (
    <group position={position} onClick={(e) => { e.stopPropagation(); onSelect(node); }}>
      {/* Outer Glow Ring if selected */}
      {isSelected && (
        <mesh>
          <sphereGeometry args={[1.3, 32, 32]} />
          <meshBasicMaterial color="#00f0ff" wireframe transparent opacity={0.4} />
        </mesh>
      )}

      {/* Main Node Mesh */}
      <mesh ref={meshRef}>
        {node.type === 'bus' ? (
          <boxGeometry args={[1.6, 1.6, 1.6]} />
        ) : node.type === 'engine' ? (
          <octahedronGeometry args={[1.1]} />
        ) : (
          <sphereGeometry args={[0.9, 32, 32]} />
        )}
        <meshStandardMaterial
          color={statusColor}
          emissive={statusColor}
          emissiveIntensity={isSelected ? 0.6 : 0.25}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>

      {/* Dynamic 3D Label */}
      <Text
        position={[0, 1.5, 0]}
        fontSize={0.45}
        color="#f8fafc"
        anchorX="center"
        anchorY="bottom"
      >
        {node.name}
      </Text>

      {/* Implementation Pill */}
      {node.implementation_type === 'stub' && (
        <Html position={[0, -1.3, 0]} center>
          <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[9px] font-mono font-bold whitespace-nowrap">
            STUB
          </span>
        </Html>
      )}
    </group>
  );
}

interface AnimatedParticleProps {
  startPos: [number, number, number];
  endPos: [number, number, number];
  color?: string;
}

function AnimatedParticle({ startPos, endPos, color = '#00f0ff' }: AnimatedParticleProps) {
  const particleRef = useRef<THREE.Mesh>(null!);

  useFrame(({ clock }) => {
    if (particleRef.current) {
      const progress = (clock.getElapsedTime() * 2) % 1;
      const x = THREE.MathUtils.lerp(startPos[0], endPos[0], progress);
      const y = THREE.MathUtils.lerp(startPos[1], endPos[1], progress);
      const z = THREE.MathUtils.lerp(startPos[2], endPos[2], progress);
      particleRef.current.position.set(x, y, z);
    }
  });

  return (
    <mesh ref={particleRef}>
      <sphereGeometry args={[0.25, 16, 16]} />
      <meshBasicMaterial color={color} />
    </mesh>
  );
}

interface Edge3DProps {
  sourcePos: [number, number, number];
  targetPos: [number, number, number];
  isActive: boolean;
}

function Edge3D({ sourcePos, targetPos, isActive }: Edge3DProps) {
  const points = useMemo(
    () => [new THREE.Vector3(...sourcePos), new THREE.Vector3(...targetPos)],
    [sourcePos, targetPos]
  );

  const lineGeometry = useMemo(() => new THREE.BufferGeometry().setFromPoints(points), [points]);

  return (
    <group>
      {/* Edge Line */}
      <primitive
        object={
          new THREE.Line(
            lineGeometry,
            new THREE.LineBasicMaterial({
              color: isActive ? '#00f0ff' : '#334155',
              linewidth: isActive ? 2 : 1,
              transparent: true,
              opacity: isActive ? 0.9 : 0.4,
            })
          )
        }
      />
      {/* Animated particle along active edge when event fires */}
      {isActive && <AnimatedParticle startPos={sourcePos} endPos={targetPos} />}
    </group>
  );
}

interface TopologyCanvas3DProps {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  selectedNode: TopologyNode | null;
  onSelectNode: (node: TopologyNode) => void;
  activeEvents: FlowEventItem[];
}

export function TopologyCanvas3D({
  nodes,
  edges,
  selectedNode,
  onSelectNode,
  activeEvents,
}: TopologyCanvas3DProps) {
  // Compute dynamic positions based on layer & node count
  const nodePositions = useMemo(() => {
    const posMap: Record<string, [number, number, number]> = {};
    const centerNodes = nodes.filter((n) => n.layer === 'center');
    const innerNodes = nodes.filter((n) => n.layer === 'inner' || (!n.layer && n.type === 'agent'));
    const outerNodes = nodes.filter((n) => n.layer === 'outer' || (!n.layer && n.type !== 'agent'));

    // Center layer
    centerNodes.forEach((node, idx) => {
      posMap[node.id] = [0, (idx - (centerNodes.length - 1) / 2) * 2.5, 0];
    });

    // Inner ring (Radius 6)
    const R_inner = 6.5;
    innerNodes.forEach((node, idx) => {
      const angle = (idx / innerNodes.length) * Math.PI * 2;
      posMap[node.id] = [Math.cos(angle) * R_inner, Math.sin(angle) * R_inner * 0.5, Math.sin(angle) * R_inner];
    });

    // Outer ring (Radius 10)
    const R_outer = 11.0;
    outerNodes.forEach((node, idx) => {
      const angle = (idx / Math.max(1, outerNodes.length)) * Math.PI * 2 + Math.PI / 4;
      posMap[node.id] = [Math.cos(angle) * R_outer, (idx % 2 === 0 ? 2 : -2), Math.sin(angle) * R_outer];
    });

    return posMap;
  }, [nodes]);

  // Set of active edges from recent flow events
  const activeEdgeKeys = useMemo(() => {
    const set = new Set<string>();
    activeEvents.forEach((evt) => {
      set.add(`${evt.source_node}->${evt.target_node}`);
    });
    return set;
  }, [activeEvents]);

  return (
    <Canvas
      camera={{ position: [0, 8, 18], fov: 50 }}
      style={{ background: 'transparent' }}
      onPointerDown={() => onSelectNode(null as any)}
    >
      <ambientLight intensity={0.7} />
      <directionalLight position={[10, 15, 10]} intensity={1.2} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />

      <OrbitControls enablePan enableZoom enableRotate maxPolarAngle={Math.PI / 2} />

      {/* Render Edges */}
      {edges.map((edge) => {
        const srcPos = nodePositions[edge.source] || [0, 0, 0];
        const tgtPos = nodePositions[edge.target] || [0, 0, 0];
        const isActive = activeEdgeKeys.has(`${edge.source}->${edge.target}`);

        return (
          <Edge3D
            key={`${edge.source}->${edge.target}`}
            sourcePos={srcPos}
            targetPos={tgtPos}
            isActive={isActive}
          />
        );
      })}

      {/* Render Nodes */}
      {nodes.map((node) => {
        const pos = nodePositions[node.id] || [0, 0, 0];
        const isSelected = selectedNode?.id === node.id;

        return (
          <NodeMesh
            key={node.id}
            node={node}
            position={pos}
            isSelected={isSelected}
            onSelect={onSelectNode}
          />
        );
      })}
    </Canvas>
  );
}
