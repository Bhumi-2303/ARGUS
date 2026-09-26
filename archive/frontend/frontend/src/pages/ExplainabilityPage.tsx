import React, { useState, useEffect, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import {
  Sparkles,
  Eye,
  BrainCircuit,
  Box
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

import { Explanation } from '../types';
import { getExplanations } from '../services/api';

/**
 * Supplementary 3D "Feature Space Vector Representation" visual
 */
const FeatureSpace3D: React.FC = () => {
  const meshRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.3;
      meshRef.current.rotation.x = Math.sin(state.clock.getElapsedTime() * 0.2) * 0.15;
    }
  });

  return (
    <Canvas camera={{ position: [0, 0, 4.2], fov: 50 }}>
      <ambientLight intensity={0.7} />
      <pointLight position={[5, 5, 5]} intensity={1.2} color="#a855f7" />
      <group ref={meshRef}>
        {/* Outer Bounding Box */}
        <mesh>
          <boxGeometry args={[2.2, 2.2, 2.2]} />
          <meshBasicMaterial color="#a855f7" wireframe transparent opacity={0.35} />
        </mesh>

        {/* Feature Nodes in Latent Space */}
        <mesh position={[0.7, 0.6, 0.4]}>
          <sphereGeometry args={[0.14, 16, 16]} />
          <meshBasicMaterial color="#ef4444" />
        </mesh>
        <mesh position={[-0.6, -0.5, -0.3]}>
          <sphereGeometry args={[0.14, 16, 16]} />
          <meshBasicMaterial color="#22d3ee" />
        </mesh>
        <mesh position={[0.3, -0.7, 0.5]}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshBasicMaterial color="#22c55e" />
        </mesh>
        <mesh position={[-0.7, 0.4, 0.2]}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshBasicMaterial color="#eab308" />
        </mesh>
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.16, 16, 16]} />
          <meshBasicMaterial color="#a855f7" />
        </mesh>
      </group>
    </Canvas>
  );
};

export const ExplainabilityPage: React.FC = () => {
  const [explanationsList, setExplanationsList] = useState<Explanation[]>([]);
  const [selectedAlertId, setSelectedAlertId] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let mounted = true;
    async function loadXAI() {
      try {
        const data = await getExplanations();
        if (mounted && data.length > 0) {
          setExplanationsList(data);
          setSelectedAlertId(data[0].alertId);
          setLoading(false);
        }
      } catch (err) {
        console.error('Failed to load explanations:', err);
        if (mounted) setLoading(false);
      }
    }
    loadXAI();

    return () => {
      mounted = false;
    };
  }, []);

  const activeExplanation = explanationsList.find((e) => e.alertId === selectedAlertId) || explanationsList[0];

  if (loading) {
    return (
      <div className="p-12 text-center text-text-secondary font-mono text-xs flex flex-col items-center justify-center gap-3">
        <div className="w-6 h-6 border-2 border-info border-t-transparent rounded-full animate-spin" />
        <span>Loading SHAP feature attribution data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 select-none">
      {/* Top Header & Alert Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">XAI & SHAP Explainability</h1>
          <p className="text-xs font-mono text-text-secondary mt-1">
            FEATURE ATTRIBUTION ENGINE & MITRE ATT&CK TAXONOMY VECTOR SEARCH
          </p>
        </div>

        {/* Alert Selector Dropdown */}
        <div className="flex items-center gap-2 self-start md:self-center">
          <span className="text-xs font-mono text-text-secondary">SELECT INCIDENT:</span>
          <select
            value={selectedAlertId}
            onChange={(e) => setSelectedAlertId(e.target.value)}
            className="px-3 py-2 rounded-lg bg-bg-surface border border-border-muted text-xs font-mono text-text-primary focus:outline-none focus:border-info cursor-pointer min-w-[200px]"
          >
            {explanationsList.map((exp) => (
              <option key={exp.alertId} value={exp.alertId}>
                {exp.alertId} — {exp.prediction.split(' (')[0]}
              </option>
            ))}
          </select>
        </div>
      </div>

      {activeExplanation && (
        <>
          {/* Header Summary Banner */}
          <div className="glass-panel-raised p-6 space-y-4 border border-border-muted">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded bg-info/20 text-info border border-info/30 text-xs font-mono font-bold">
                    {activeExplanation.alertId}
                  </span>
                  <span className="text-xs font-mono text-text-secondary">
                    CLASSIFICATION SUMMARY
                  </span>
                </div>
                <h2 className="text-xl font-bold text-text-primary">
                  {activeExplanation.prediction}
                </h2>
              </div>

              {/* Model & Confidence Pills */}
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-bg-surface border border-border-muted text-center min-w-[120px]">
                  <span className="text-[10px] font-mono text-text-secondary uppercase block">MODEL</span>
                  <span className="text-sm font-bold font-mono text-info mt-0.5 block">
                    {activeExplanation.model}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-bg-surface border border-border-muted text-center min-w-[120px]">
                  <span className="text-[10px] font-mono text-text-secondary uppercase block">CONFIDENCE</span>
                  <span className="text-xl font-bold font-mono text-safe mt-0.5 block">
                    {activeExplanation.confidence !== undefined ? `${(activeExplanation.confidence * 100).toFixed(0)}%` : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Main 2-Column Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column (2 Cols): SHAP Bar Chart & Narrative */}
            <div className="lg:col-span-2 space-y-6">
              {/* SHAP Chart Box */}
              <div className="glass-panel p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-border-muted pb-3">
                  <h3 className="text-sm font-mono font-bold tracking-wider text-text-secondary uppercase flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-info" /> SHAP FEATURE ATTRIBUTION VALUES
                  </h3>
                  <span className="text-[10px] font-mono text-text-secondary">
                    RED = PUSHES RISK UP • GREEN = REDUCES RISK
                  </span>
                </div>

                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      layout="vertical"
                      data={activeExplanation.features}
                      margin={{ top: 10, right: 30, left: 160, bottom: 5 }}
                    >
                      <XAxis type="number" stroke="#8b96a8" fontSize={11} />
                      <YAxis
                        type="category"
                        dataKey="feature"
                        stroke="#8b96a8"
                        fontSize={11}
                        tick={{ fill: '#f2f5f9' }}
                      />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0a0e17', borderColor: '#1e2635', color: '#f2f5f9' }}
                        formatter={(value: number) => [
                          `${value > 0 ? '+' : ''}${value.toFixed(2)}`,
                          'SHAP Contribution'
                        ]}
                      />
                      <Bar dataKey="contribution">
                        {activeExplanation.features.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={entry.contribution > 0 ? '#ef4444' : '#22c55e'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Feature Table Values */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono pt-2">
                  {activeExplanation.features.map((feat) => (
                    <div
                      key={feat.feature}
                      className="p-2.5 rounded-lg bg-bg-surface border border-border-muted/60 flex justify-between items-center"
                    >
                      <span className="text-text-primary truncate max-w-[180px]" title={feat.feature}>
                        {feat.feature}
                      </span>
                      <span
                        className={`font-bold ${feat.contribution > 0 ? 'text-critical' : 'text-safe'}`}
                      >
                        {feat.contribution > 0 ? '+' : ''}
                        {feat.contribution.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Narrative Box */}
              <div className="glass-panel p-6 space-y-3 border-l-4 border-l-info">
                <div className="flex items-center gap-2 text-xs font-mono font-bold text-info uppercase">
                  <Eye className="w-4 h-4 text-info" /> HUMAN-READABLE EXPLANATION NARRATIVE
                </div>
                <p className="text-sm text-text-primary leading-relaxed font-sans">
                  "{activeExplanation.narrative}"
                </p>
              </div>
            </div>

            {/* Right Column (1 Col): 3D Feature Space & MITRE Mappings */}
            <div className="space-y-6">
              {/* Decorative 3D Feature Space Panel */}
              <div className="glass-panel p-5 space-y-3 h-72 flex flex-col relative overflow-hidden">
                <div className="flex items-center justify-between border-b border-border-muted pb-2 z-10">
                  <span className="text-xs font-mono font-bold tracking-wider text-text-secondary uppercase flex items-center gap-1.5">
                    <Box className="w-4 h-4 text-xai" /> 3D FEATURE SPACE LATENT EMBEDDING
                  </span>
                  <span className="text-[9px] font-mono text-xai bg-xai/10 border border-xai/30 px-1.5 py-0.5 rounded">
                    DECORATIVE VISUAL
                  </span>
                </div>

                <div className="flex-1 w-full h-full relative">
                  <FeatureSpace3D />
                </div>
              </div>

              {/* MITRE ATT&CK for ICS Techniques */}
              <div className="glass-panel p-5 space-y-4">
                <h3 className="text-xs font-mono font-bold tracking-wider text-text-secondary uppercase flex items-center gap-2">
                  <BrainCircuit className="w-4 h-4 text-info" /> RETRIEVED MITRE ATT&CK FOR ICS
                </h3>

                <div className="space-y-3 font-mono text-xs">
                  <div className="p-3 rounded-lg bg-bg-surface border border-border-muted space-y-1">
                    <div className="flex justify-between items-center text-info font-bold">
                      <span>[T0855] Command Injection</span>
                      <span className="text-[10px] text-text-secondary">Dist: 0.65</span>
                    </div>
                    <p className="text-[11px] text-text-secondary font-sans leading-normal">
                      Adversaries send unauthorized command messages to control devices to alter process behavior.
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-bg-surface border border-border-muted space-y-1">
                    <div className="flex justify-between items-center text-info font-bold">
                      <span>[T0869] Standard Application Protocol</span>
                      <span className="text-[10px] text-text-secondary">Dist: 0.67</span>
                    </div>
                    <p className="text-[11px] text-text-secondary font-sans leading-normal">
                      Adversaries manipulate standard SCADA protocols (IEC-104, Modbus) to blend malicious traffic.
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-bg-surface border border-border-muted space-y-1">
                    <div className="flex justify-between items-center text-info font-bold">
                      <span>[T0885] Commonly Used Port</span>
                      <span className="text-[10px] text-text-secondary">Dist: 0.69</span>
                    </div>
                    <p className="text-[11px] text-text-secondary font-sans leading-normal">
                      Targeting standard communication ports (TCP 2404 for IEC-104) to access field devices.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ExplainabilityPage;
