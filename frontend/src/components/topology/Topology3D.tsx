import React, { useState, useEffect, useRef } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { Box, Network as NetworkIcon, List } from 'lucide-react';

import { NetworkNode, NetworkConnection } from '../../types';
import { getNetworkNodes, getNetworkConnections } from '../../services/api';
import { networkNodes as initialNodes, networkConnections as initialConnections } from '../../data/mockData';

import Node3DModel from './Node3DModel';
import Connection3DLine from './Connection3DLine';
import LegendOverlay from './LegendOverlay';
import NodeDetailDrawer from './NodeDetailDrawer';
import FlatTopology2D from './FlatTopology2D';
import NodeListView from './NodeListView';

export type ViewMode = '3d' | '2d' | 'list';

interface Topology3DProps {
  className?: string;
  initialSelectedNodeId?: string;
}

/**
 * Helper component inside Canvas to handle smooth camera refocusing on selected node
 */
const CameraController: React.FC<{
  selectedNode: NetworkNode | null;
  controlsRef: React.RefObject<OrbitControlsImpl | null>;
}> = ({ selectedNode, controlsRef }) => {
  const { camera } = useThree();

  useEffect(() => {
    if (selectedNode && controlsRef.current) {
      const { x, y, z } = selectedNode.position;
      // Animate orbit target towards node position
      controlsRef.current.target.set(x, y, z);
      controlsRef.current.update();
    }
  }, [selectedNode, camera, controlsRef]);

  return null;
};

export const Topology3D: React.FC<Topology3DProps> = ({
  className = '',
  initialSelectedNodeId
}) => {
  const [nodes, setNodes] = useState<NetworkNode[]>(initialNodes);
  const [connections, setConnections] = useState<NetworkConnection[]>(initialConnections);
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('3d');
  const [reducedMotion, setReducedMotion] = useState<boolean>(false);

  const controlsRef = useRef<OrbitControlsImpl | null>(null);

  // Fetch data asynchronously via api service
  useEffect(() => {
    let mounted = true;
    async function loadData() {
      try {
        const [fetchedNodes, fetchedConns] = await Promise.all([
          getNetworkNodes(),
          getNetworkConnections()
        ]);
        if (mounted && fetchedNodes.length > 0) {
          setNodes(fetchedNodes);
          setConnections(fetchedConns);

          if (initialSelectedNodeId) {
            const initial = fetchedNodes.find((n) => n.id === initialSelectedNodeId);
            if (initial) setSelectedNode(initial);
          }
        }
      } catch (err) {
        console.warn('Using mock data fallback for topology:', err);
      }
    }
    loadData();

    // Check prefers-reduced-motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mediaQuery.matches);

    const handleMotionChange = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handleMotionChange);

    return () => {
      mounted = false;
      mediaQuery.removeEventListener('change', handleMotionChange);
    };
  }, [initialSelectedNodeId]);

  // Handle Esc key to close drawer
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSelectedNode(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSelectNode = (node: NetworkNode) => {
    setSelectedNode(node);
  };

  return (
    <div className={`relative w-full h-full min-h-[500px] bg-bg-void overflow-hidden select-none ${className}`}>
      {/* Top-Right View Mode Toggle Bar */}
      <div className="absolute top-4 right-4 z-20 flex items-center bg-bg-surface-raised/90 border border-border-muted rounded-lg p-1 shadow-lg backdrop-blur-md">
        <button
          onClick={() => setViewMode('3d')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all ${
            viewMode === '3d'
              ? 'bg-info/20 text-info border border-info/40 font-bold'
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          <Box className="w-3.5 h-3.5" />
          <span>3D View</span>
        </button>

        <button
          onClick={() => setViewMode('2d')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all ${
            viewMode === '2d'
              ? 'bg-info/20 text-info border border-info/40 font-bold'
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          <NetworkIcon className="w-3.5 h-3.5" />
          <span>Topology View</span>
        </button>

        <button
          onClick={() => setViewMode('list')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all ${
            viewMode === 'list'
              ? 'bg-info/20 text-info border border-info/40 font-bold'
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          <List className="w-3.5 h-3.5" />
          <span>List View</span>
        </button>
      </div>

      {/* Main View Area */}
      {viewMode === '3d' && (
        <>
          <Canvas
            camera={{ position: [12, 14, 16], fov: 45 }}
            className="w-full h-full"
            gl={{ antialias: true, toneMappingExposure: 1.2 }}
            onPointerMissed={() => setSelectedNode(null)}
          >
            <color attach="background" args={['#05070d']} />

            {/* Lighting */}
            <ambientLight intensity={0.7} />
            <directionalLight position={[15, 25, 15]} intensity={1.3} color="#ffffff" castShadow={false} />
            <pointLight position={[-10, 10, -10]} intensity={0.5} color="#22d3ee" />

            {/* Orbit Controls */}
            <OrbitControls
              ref={controlsRef}
              makeDefault
              enableDamping
              dampingFactor={0.05}
              minDistance={5}
              maxDistance={40}
              maxPolarAngle={Math.PI / 2 - 0.05}
            />

            <CameraController selectedNode={selectedNode} controlsRef={controlsRef} />

            {/* Render 3D Connections */}
            {connections.map((conn) => {
              const source = nodes.find((n) => n.id === conn.sourceId);
              const target = nodes.find((n) => n.id === conn.targetId);
              if (!source || !target) return null;

              return (
                <Connection3DLine
                  key={conn.id}
                  connection={conn}
                  sourceNode={source}
                  targetNode={target}
                  reducedMotion={reducedMotion}
                />
              );
            })}

            {/* Render 3D Nodes */}
            {nodes.map((node) => (
              <Node3DModel
                key={node.id}
                node={node}
                isSelected={selectedNode?.id === node.id}
                onSelect={handleSelectNode}
                reducedMotion={reducedMotion}
              />
            ))}
          </Canvas>

          {/* Legend Overlay */}
          <LegendOverlay />
        </>
      )}

      {viewMode === '2d' && (
        <FlatTopology2D
          nodes={nodes}
          connections={connections}
          selectedNode={selectedNode}
          onSelectNode={handleSelectNode}
        />
      )}

      {viewMode === 'list' && (
        <NodeListView
          nodes={nodes}
          selectedNode={selectedNode}
          onSelectNode={handleSelectNode}
        />
      )}

      {/* Node Detail Drawer */}
      <NodeDetailDrawer
        node={selectedNode}
        allNodes={nodes}
        onClose={() => setSelectedNode(null)}
        onSelectNode={handleSelectNode}
      />
    </div>
  );
};

export default Topology3D;
