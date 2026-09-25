import React, { useMemo } from 'react';
import { TopologyNode, TopologyEdge, FlowEventItem } from '../../api/client';

interface TopologyGraph2DProps {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  selectedNode: TopologyNode | null;
  onSelectNode: (node: TopologyNode) => void;
  activeEvents: FlowEventItem[];
}

export function TopologyGraph2D({
  nodes,
  edges,
  selectedNode,
  onSelectNode,
  activeEvents,
}: TopologyGraph2DProps) {
  // 2D SVG canvas dimensions
  const width = 800;
  const height = 500;
  const centerX = width / 2;
  const centerY = height / 2;

  // Calculate 2D coordinates for nodes based on layer
  const nodeCoords = useMemo(() => {
    const map: Record<string, { x: number; y: number }> = {};
    const centerNodes = nodes.filter((n) => n.layer === 'center');
    const innerNodes = nodes.filter((n) => n.layer === 'inner' || (!n.layer && n.type === 'agent'));
    const outerNodes = nodes.filter((n) => n.layer === 'outer' || (!n.layer && n.type !== 'agent'));

    // Center
    centerNodes.forEach((n, idx) => {
      map[n.id] = { x: centerX, y: centerY + (idx - (centerNodes.length - 1) / 2) * 80 };
    });

    // Inner ring
    const rInner = 160;
    innerNodes.forEach((n, idx) => {
      const angle = (idx / innerNodes.length) * Math.PI * 2 - Math.PI / 2;
      map[n.id] = {
        x: centerX + Math.cos(angle) * rInner,
        y: centerY + Math.sin(angle) * rInner,
      };
    });

    // Outer ring
    const rOuter = 230;
    outerNodes.forEach((n, idx) => {
      const angle = (idx / Math.max(1, outerNodes.length)) * Math.PI * 2 + Math.PI / 4;
      map[n.id] = {
        x: centerX + Math.cos(angle) * rOuter,
        y: centerY + Math.sin(angle) * rOuter,
      };
    });

    return map;
  }, [nodes, centerX, centerY]);

  const activeEdgeKeys = useMemo(() => {
    const set = new Set<string>();
    activeEvents.forEach((evt) => {
      set.add(`${evt.source_node}->${evt.target_node}`);
    });
    return set;
  }, [activeEvents]);

  return (
    <div className="w-full h-full relative bg-slate-950/60 rounded-xl overflow-hidden border border-slate-800 flex items-center justify-center p-4">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full max-h-[550px]">
        {/* Render Edges */}
        {edges.map((edge) => {
          const src = nodeCoords[edge.source] || { x: centerX, y: centerY };
          const tgt = nodeCoords[edge.target] || { x: centerX, y: centerY };
          const isActive = activeEdgeKeys.has(`${edge.source}->${edge.target}`);

          return (
            <g key={`${edge.source}->${edge.target}`}>
              <line
                x1={src.x}
                y1={src.y}
                x2={tgt.x}
                y2={tgt.y}
                stroke={isActive ? '#00f0ff' : '#334155'}
                strokeWidth={isActive ? 3 : 1.5}
                strokeDasharray={isActive ? '6 3' : 'none'}
                className={isActive ? 'animate-pulse' : ''}
              />
            </g>
          );
        })}

        {/* Render Nodes */}
        {nodes.map((node) => {
          const pos = nodeCoords[node.id] || { x: centerX, y: centerY };
          const isSelected = selectedNode?.id === node.id;

          const fillColor =
            node.status === 'busy'
              ? '#10b981'
              : node.status === 'blocked'
              ? '#f59e0b'
              : node.status === 'failed'
              ? '#f43f5e'
              : node.type === 'bus'
              ? '#06b6d4'
              : node.type === 'engine'
              ? '#8b5cf6'
              : '#3b82f6';

          return (
            <g
              key={node.id}
              transform={`translate(${pos.x}, ${pos.y})`}
              onClick={() => onSelectNode(node)}
              className="cursor-pointer group"
            >
              {/* Selection Ring */}
              {isSelected && (
                <circle r={28} fill="none" stroke="#00f0ff" strokeWidth={2} strokeDasharray="4 2" className="animate-spin" />
              )}

              {/* Node Shape */}
              <circle
                r={20}
                fill={fillColor}
                fillOpacity={0.2}
                stroke={fillColor}
                strokeWidth={2}
                className="group-hover:scale-110 transition-transform"
              />
              <circle r={8} fill={fillColor} />

              {/* Node Label */}
              <text
                y={34}
                textAnchor="middle"
                fill="#f8fafc"
                fontSize={11}
                fontFamily="monospace"
                fontWeight="bold"
              >
                {node.name}
              </text>

              {/* Stub Badge */}
              {node.implementation_type === 'stub' && (
                <text
                  y={-24}
                  textAnchor="middle"
                  fill="#f59e0b"
                  fontSize={9}
                  fontFamily="monospace"
                  fontWeight="bold"
                >
                  STUB
                </text>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
