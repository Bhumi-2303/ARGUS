import React from 'react';
import { NetworkNode, NetworkConnection } from '../../types';
import { STATUS_COLORS } from './Node3DModel';

interface Flat2DProps {
  nodes: NetworkNode[];
  connections: NetworkConnection[];
  selectedNode: NetworkNode | null;
  onSelectNode: (node: NetworkNode) => void;
}

export const FlatTopology2D: React.FC<Flat2DProps> = ({
  nodes,
  connections,
  selectedNode,
  onSelectNode
}) => {
  // Map 3D position (x, z) to 2D SVG coordinates (cx, cy)
  const mapPos = (pos: { x: number; y: number; z: number }) => {
    // Range x: -14 to 8 -> SVG x: 100 to 900
    // Range z: -9 to 8 -> SVG y: 100 to 550
    const cx = 500 + pos.x * 28;
    const cy = 320 + pos.z * 24;
    return { cx, cy };
  };

  return (
    <div className="w-full h-full bg-bg-void relative overflow-auto p-4 flex items-center justify-center">
      <svg className="w-full h-full min-w-[800px] min-h-[600px] select-none" viewBox="0 0 1000 650">
        {/* Background Grid Pattern */}
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e2635" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />

        {/* Connections */}
        {connections.map((conn) => {
          const source = nodes.find((n) => n.id === conn.sourceId);
          const target = nodes.find((n) => n.id === conn.targetId);
          if (!source || !target) return null;

          const p1 = mapPos(source.position);
          const p2 = mapPos(target.position);
          const isSuspicious = conn.trafficType === 'suspicious';

          return (
            <g key={conn.id}>
              <line
                x1={p1.cx}
                y1={p1.cy}
                x2={p2.cx}
                y2={p2.cy}
                stroke={isSuspicious ? '#ef4444' : '#22d3ee'}
                strokeWidth={isSuspicious ? '2.5' : '1.5'}
                strokeDasharray={isSuspicious ? '6,6' : undefined}
                opacity={isSuspicious ? 0.9 : 0.4}
              />
            </g>
          );
        })}

        {/* Nodes */}
        {nodes.map((node) => {
          const { cx, cy } = mapPos(node.position);
          const isSelected = selectedNode?.id === node.id;
          const statusStyle = STATUS_COLORS[node.status] || STATUS_COLORS.secure;

          return (
            <g
              key={node.id}
              onClick={() => onSelectNode(node)}
              className="cursor-pointer group"
              transform={`translate(${cx}, ${cy})`}
            >
              {/* Selection Ring */}
              {isSelected && (
                <circle r="22" fill="none" stroke="#22d3ee" strokeWidth="2" className="animate-pulse" />
              )}

              {/* Node Outer Base Circle */}
              <circle
                r="16"
                fill="#0a0e17"
                stroke={statusStyle.color}
                strokeWidth="2.5"
                className="transition-transform group-hover:scale-110"
              />

              {/* Status Center Dot */}
              <circle r="6" fill={statusStyle.color} />

              {/* Node Label */}
              <text
                y="32"
                textAnchor="middle"
                fill="#f2f5f9"
                fontSize="11"
                fontWeight="600"
                fontFamily="monospace"
              >
                {node.name}
              </text>
              <text
                y="45"
                textAnchor="middle"
                fill={statusStyle.color}
                fontSize="9"
                fontWeight="700"
                fontFamily="monospace"
                className="uppercase"
              >
                {node.status}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

export default FlatTopology2D;
