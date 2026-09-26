import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { NetworkConnection, NetworkNode } from '../../types';

interface Connection3DProps {
  connection: NetworkConnection;
  sourceNode: NetworkNode;
  targetNode: NetworkNode;
  reducedMotion: boolean;
}

export const Connection3DLine: React.FC<Connection3DProps> = ({
  connection,
  sourceNode,
  targetNode,
  reducedMotion
}) => {
  const pulseRef = useRef<THREE.Mesh>(null);

  const isSuspicious = connection.trafficType === 'suspicious';
  const color = isSuspicious ? '#ef4444' : '#22d3ee';

  // Compute 3D positions & curve path
  const { startVec, curve } = useMemo(() => {
    const start = new THREE.Vector3(
      sourceNode.position.x,
      sourceNode.position.y + 0.3,
      sourceNode.position.z
    );
    const end = new THREE.Vector3(
      targetNode.position.x,
      targetNode.position.y + 0.3,
      targetNode.position.z
    );

    // Slightly arch the line upward in the middle for 3D depth
    const mid = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
    mid.y += Math.min(start.distanceTo(end) * 0.15, 1.2);

    const catmullCurve = new THREE.CatmullRomCurve3([start, mid, end]);
    return { startVec: start, curve: catmullCurve };
  }, [sourceNode.position, targetNode.position]);

  // Points for Line Rendering
  const points = useMemo(() => {
    return curve.getPoints(24);
  }, [curve]);

  const lineGeometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [points]);

  // Animate pulse along the line for data flow effect
  useFrame((state) => {
    if (reducedMotion || !pulseRef.current) return;
    const speed = isSuspicious ? 1.2 : 0.6;
    const t = (state.clock.getElapsedTime() * speed) % 1;
    const pos = curve.getPoint(t);
    pulseRef.current.position.copy(pos);
  });

  return (
    <group>
      {/* 3D Line Connection */}
      <primitive
        object={
          new THREE.Line(
            lineGeometry,
            new THREE.LineBasicMaterial({
              color: new THREE.Color(color),
              linewidth: isSuspicious ? 2 : 1,
              transparent: true,
              opacity: isSuspicious ? 0.85 : 0.5
            })
          )
        }
      />

      {/* Flowing Data Pulse Sphere */}
      <mesh ref={pulseRef} position={startVec}>
        <sphereGeometry args={[isSuspicious ? 0.12 : 0.08, 12, 12]} />
        <meshBasicMaterial color={color} transparent opacity={0.9} />
      </mesh>
    </group>
  );
};

export default Connection3DLine;
