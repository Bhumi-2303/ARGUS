import React, { useMemo } from 'react';
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
} from 'lucide-react';
import { TopologyNode, TopologyEdge, FlowEventItem } from '../../api/client';

export interface TopologyGraph2DProps {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  selectedNode: TopologyNode | null;
  onSelectNode: (node: TopologyNode) => void;
  activeEvents: FlowEventItem[];
  layoutMode?: 'architecture' | 'topology';
}

function getNodeIcon(id: string) {
  switch (id.toLowerCase()) {
    case 'orchestrator':
      return Workflow;
    case 'data_intelligence':
      return Database;
    case 'threat_analysis':
      return Crosshair;
    case 'explainability':
      return BarChart3;
    case 'knowledge_context':
      return BookOpen;
    case 'risk_prediction':
      return AlertTriangle;
    case 'decision_support':
      return ShieldCheck;
    case 'api_gateway':
      return Radio;
    case 'message_bus':
      return Zap;
    case 'policy_engine':
      return Lock;
    default:
      return Cpu;
  }
}

function getNodeTheme(id: string, type: string) {
  switch (id.toLowerCase()) {
    case 'orchestrator':
      return { stroke: '#00f0ff', fill: '#08172e', glow: '#00f0ff' };
    case 'data_intelligence':
      return { stroke: '#06b6d4', fill: '#061a29', glow: '#06b6d4' };
    case 'threat_analysis':
      return { stroke: '#f43f5e', fill: '#250b14', glow: '#f43f5e' };
    case 'explainability':
      return { stroke: '#a855f7', fill: '#1b0a2a', glow: '#a855f7' };
    case 'knowledge_context':
      return { stroke: '#3b82f6', fill: '#0a142e', glow: '#3b82f6' };
    case 'risk_prediction':
      return { stroke: '#f59e0b', fill: '#271905', glow: '#f59e0b' };
    case 'decision_support':
      return { stroke: '#10b981', fill: '#061f18', glow: '#10b981' };
    case 'api_gateway':
      return { stroke: '#38bdf8', fill: '#081c2d', glow: '#38bdf8' };
    case 'message_bus':
      return { stroke: '#00f0ff', fill: '#06202e', glow: '#00f0ff' };
    case 'policy_engine':
      return { stroke: '#6366f1', fill: '#10112d', glow: '#6366f1' };
    default:
      return { stroke: '#38bdf8', fill: '#0f172a', glow: '#38bdf8' };
  }
}

export function TopologyGraph2D({
  nodes,
  edges,
  selectedNode,
  onSelectNode,
  activeEvents,
  layoutMode = 'architecture',
}: TopologyGraph2DProps) {
  const width = 900;
  const height = 540;
  const centerX = width / 2;
  const centerY = height / 2;

  // Calculate coordinates based on layout mode
  const nodeCoords = useMemo(() => {
    const map: Record<string, { x: number; y: number; r: number }> = {};

    if (layoutMode === 'architecture') {
      // 1. ARGUS Orchestrator in center
      map['orchestrator'] = { x: centerX, y: centerY, r: 36 };

      // 2. The 6 specialized agents in an orbital ring (Radius 180)
      const agentIds = [
        'data_intelligence',
        'threat_analysis',
        'explainability',
        'knowledge_context',
        'risk_prediction',
        'decision_support',
      ];
      const rAgents = 185;
      agentIds.forEach((id, idx) => {
        const angle = (idx / agentIds.length) * Math.PI * 2;
        map[id] = {
          x: centerX + Math.cos(angle) * rAgents,
          y: centerY + Math.sin(angle) * rAgents,
          r: 28,
        };
      });

      // 3. Infrastructure components on outer positions
      map['api_gateway'] = { x: 90, y: centerY - 60, r: 24 };
      map['message_bus'] = { x: 230, y: centerY + 70, r: 24 };
      map['policy_engine'] = { x: width - 90, y: centerY, r: 24 };

      // Any remaining nodes
      nodes.forEach((n, idx) => {
        if (!map[n.id]) {
          map[n.id] = { x: width - 120, y: 80 + idx * 60, r: 22 };
        }
      });
    } else {
      // System Topology Flow Mode: Left-to-Right Pipeline
      map['api_gateway'] = { x: 80, y: centerY, r: 24 };
      map['message_bus'] = { x: 200, y: centerY, r: 24 };
      map['orchestrator'] = { x: 330, y: centerY, r: 34 };

      map['data_intelligence'] = { x: 470, y: centerY - 140, r: 26 };
      map['threat_analysis'] = { x: 470, y: centerY + 140, r: 26 };
      map['explainability'] = { x: 610, y: centerY + 140, r: 26 };
      map['knowledge_context'] = { x: 610, y: centerY - 140, r: 26 };
      map['risk_prediction'] = { x: 740, y: centerY - 70, r: 26 };
      map['decision_support'] = { x: 740, y: centerY + 70, r: 26 };

      map['policy_engine'] = { x: 840, y: centerY, r: 24 };

      nodes.forEach((n, idx) => {
        if (!map[n.id]) {
          map[n.id] = { x: width - 100, y: 80 + idx * 50, r: 22 };
        }
      });
    }

    return map;
  }, [nodes, centerX, centerY, width, layoutMode]);

  const activeEdgeKeys = useMemo(() => {
    const set = new Set<string>();
    activeEvents.forEach((evt) => {
      set.add(`${evt.source_node}->${evt.target_node}`);
    });
    return set;
  }, [activeEvents]);

  // Orchestrator radial communication links
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
    <div className="w-full h-full relative bg-[#020617] rounded-xl overflow-hidden border border-slate-800 flex items-center justify-center p-2 select-none">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full max-h-[550px]">
        <defs>
          {/* Cyber Background Grid */}
          <pattern id="cyber-grid-2d" width="36" height="36" patternUnits="userSpaceOnUse">
            <path d="M 36 0 L 0 0 0 36" fill="none" stroke="#0f172a" strokeWidth="1" />
            <circle cx="0" cy="0" r="1.5" fill="#0284c7" opacity="0.4" />
          </pattern>

          {/* Glow Filters */}
          <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Technical Grid Rect */}
        <rect width={width} height={height} fill="url(#cyber-grid-2d)" />

        {/* Concentric Radar / Orbital Rings (in Architecture mode) */}
        {layoutMode === 'architecture' && (
          <g opacity="0.35">
            <circle cx={centerX} cy={centerY} r="185" fill="none" stroke="#00f0ff" strokeWidth="1.5" strokeDasharray="6 6" />
            <circle cx={centerX} cy={centerY} r="280" fill="none" stroke="#3b82f6" strokeWidth="1" strokeDasharray="3 6" />
            <circle cx={centerX} cy={centerY} r="70" fill="none" stroke="#00f0ff" strokeWidth="1" opacity="0.5" />
          </g>
        )}

        {/* Radial Orchestrator Control Lines */}
        {orchestratorAgentLinks.map((agentId) => {
          const src = nodeCoords['orchestrator'] || { x: centerX, y: centerY };
          const tgt = nodeCoords[agentId];
          if (!tgt) return null;
          const isActive = activeEvents.some(
            (e) => e.target_node === agentId || e.source_node === agentId
          );

          return (
            <line
              key={`orch-link-${agentId}`}
              x1={src.x}
              y1={src.y}
              x2={tgt.x}
              y2={tgt.y}
              stroke={isActive ? '#00f0ff' : '#1e293b'}
              strokeWidth={isActive ? 2.5 : 1}
              strokeDasharray={isActive ? '4 4' : '2 4'}
              className={isActive ? 'animate-pulse' : ''}
              opacity={isActive ? 0.9 : 0.4}
            />
          );
        })}

        {/* Render Sequential Edges */}
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
                stroke={isActive ? '#10b981' : '#334155'}
                strokeWidth={isActive ? 3 : 1.5}
                strokeDasharray={isActive ? '8 4' : 'none'}
                className={isActive ? 'animate-pulse' : ''}
              />
            </g>
          );
        })}

        {/* Render Nodes as Cyber Platforms */}
        {nodes.map((node) => {
          const pos = nodeCoords[node.id] || { x: centerX, y: centerY, r: 24 };
          const isSelected = selectedNode?.id === node.id;
          const theme = getNodeTheme(node.id, node.type);
          const IconComponent = getNodeIcon(node.id);

          return (
            <g
              key={node.id}
              className="cursor-pointer transition-transform duration-200"
              onClick={() => onSelectNode(node)}
            >
              {/* Outer Selection Aura */}
              {isSelected && (
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={pos.r + 14}
                  fill="none"
                  stroke="#00f0ff"
                  strokeWidth="2"
                  strokeDasharray="4 3"
                  className="animate-spin"
                  style={{ transformOrigin: `${pos.x}px ${pos.y}px`, animationDuration: '8s' }}
                />
              )}

              {/* Elevated Platform Outer Ring */}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={pos.r + 6}
                fill="none"
                stroke={theme.stroke}
                strokeWidth={isSelected ? '2' : '1.2'}
                opacity={isSelected ? 0.9 : 0.4}
              />

              {/* Base Platform Disc */}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={pos.r}
                fill={theme.fill}
                stroke={theme.stroke}
                strokeWidth={isSelected ? '3' : '2'}
                filter="url(#glow-cyan)"
              />

              {/* Icon in Center */}
              <foreignObject
                x={pos.x - 12}
                y={pos.y - 12}
                width="24"
                height="24"
                className="pointer-events-none"
              >
                <div className="w-full h-full flex items-center justify-center" style={{ color: theme.stroke }}>
                  <IconComponent className="w-4 h-4" />
                </div>
              </foreignObject>

              {/* Cyber Label */}
              <text
                x={pos.x}
                y={pos.y + pos.r + 18}
                textAnchor="middle"
                className="text-[10px] font-mono font-bold fill-slate-200 pointer-events-none"
              >
                {node.name}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
