import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  PlusCircle,
  CheckCircle2,
  Sliders,
  ShieldCheck,
  Zap,
  Lock,
  ArrowRight,
  Info,
  RotateCcw,
} from 'lucide-react';
import { api, OnboardResponse } from '../../api/client';
import { ProvenanceBadge } from '../../components/ProvenanceBadge';
import { Card } from '../../components/Card';

export default function OnboardingWizardPage() {
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [targetDomain, setTargetDomain] = useState<string>('nfton');

  // Window sizes
  const [adaptSize, setAdaptSize] = useState<number>(5000);
  const [calibSize, setCalibSize] = useState<number>(2000);
  const [testSize, setTestSize] = useState<number>(3000);

  // Onboard API mutation
  const onboardMutation = useMutation({
    mutationFn: (data: {
      target_domain: string;
      adaptation_window_size: number;
      calibration_window_size: number;
      test_window_size: number;
    }) => api.onboard(data),
  });

  const handleRunOnboarding = () => {
    onboardMutation.mutate(
      {
        target_domain: targetDomain,
        adaptation_window_size: adaptSize,
        calibration_window_size: calibSize,
        test_window_size: testSize,
      },
      {
        onSuccess: () => {
          setCurrentStep(5); // Jump to final evaluation step
        },
      }
    );
  };

  const onboardResult: OnboardResponse | null = onboardMutation.data || null;

  const steps = [
    { num: 1, title: 'Adaptation Window', desc: 'Select unlabelled target flows' },
    { num: 2, title: 'CORAL Estimation', desc: 'Align target covariance matrix' },
    { num: 3, title: 'Threshold Calibration', desc: 'Sweep MCC on calibration set' },
    { num: 4, title: 'Freeze Threshold', desc: 'Lock decision threshold' },
    { num: 5, title: 'Zero-Leakage Test', desc: 'Evaluate holdout performance' },
  ];

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100 font-mono flex items-center gap-2">
            <PlusCircle className="w-6 h-6 text-cyan-400" />
            <span>Target Network Telemetry Onboarding & Calibration Wizard</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Simulate demo-scale target network domain adaptation, CORAL covariance alignment, and decision threshold freezing.
          </p>
        </div>

        <ProvenanceBadge
          sourceFile="data/samples/nfton.parquet"
          protocolStatus="demo-scale"
        />
      </div>

      {/* Demo Scale Notice Banner */}
      <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 flex items-start gap-3 shadow-lg">
        <Info className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs font-mono">
          <div className="font-bold text-slate-100 flex items-center gap-2">
            <span>ℹ️ DEMO-SCALE ONBOARDING SIMULATION</span>
            <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-[10px]">
              PROTOCOL: DEMO SCALE
            </span>
          </div>
          <p className="text-cyan-200/90 leading-relaxed font-sans">
            This wizard performs fast demo-scale covariance matrix calculation and threshold optimization over sample batches directly in memory. Full-scale production training pipeline scripts are located in <code>experiments/training/</code>.
          </p>
        </div>
      </div>

      {/* Step Indicator Progress Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
        {steps.map((step) => {
          const isActive = currentStep === step.num;
          const isDone = currentStep > step.num;

          return (
            <div
              key={step.num}
              onClick={() => setCurrentStep(step.num)}
              className={`p-3 rounded-xl border text-xs font-mono cursor-pointer transition-all duration-200 ${
                isActive
                  ? 'bg-cyan-500/10 border-cyan-500/60 text-cyan-300 shadow-md shadow-cyan-500/10'
                  : isDone
                  ? 'bg-slate-900/80 border-slate-800 text-emerald-400'
                  : 'bg-slate-950/60 border-slate-800/80 text-slate-500 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-[10px]">STEP 0{step.num}</span>
                {isDone ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-cyan-400 animate-pulse' : 'bg-slate-700'}`} />
                )}
              </div>
              <div className="font-bold text-slate-200 truncate">{step.title}</div>
              <div className="text-[10px] text-slate-400 truncate mt-0.5">{step.desc}</div>
            </div>
          );
        })}
      </div>

      {/* Step Content Cards */}
      <Card className="space-y-6">
        {currentStep === 1 && (
          <div className="space-y-4">
            <h2 className="text-base font-bold font-mono text-slate-100 flex items-center gap-2">
              <Sliders className="w-5 h-5 text-cyan-400" />
              <span>Step 1: Select Target Network Domain & Window Sizes</span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-mono text-xs">
              <div className="space-y-3">
                <div>
                  <label htmlFor="onboard-domain-select" className="text-slate-400 block mb-1">
                    Target Domain:
                  </label>
                  <select
                    id="onboard-domain-select"
                    value={targetDomain}
                    onChange={(e) => setTargetDomain(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
                  >
                    <option value="nfton">NF-ToN-IoT-v2 (Smart Home / Industrial IoT)</option>
                    <option value="iec104">IEC 60870-5-104 (Power Grid SCADA Substation)</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="adapt-size-input" className="text-slate-400 block mb-1">
                    Adaptation Sample Size (Unlabelled Flows):
                  </label>
                  <input
                    id="adapt-size-input"
                    type="number"
                    value={adaptSize}
                    onChange={(e) => setAdaptSize(Number(e.target.value))}
                    className="w-full px-3 py-1.5 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <label htmlFor="calib-size-input" className="text-slate-400 block mb-1">
                    Calibration Window Size:
                  </label>
                  <input
                    id="calib-size-input"
                    type="number"
                    value={calibSize}
                    onChange={(e) => setCalibSize(Number(e.target.value))}
                    className="w-full px-3 py-1.5 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label htmlFor="test-size-input" className="text-slate-400 block mb-1">
                    Holdout Test Window Size:
                  </label>
                  <input
                    id="test-size-input"
                    type="number"
                    value={testSize}
                    onChange={(e) => setTestSize(Number(e.target.value))}
                    className="w-full px-3 py-1.5 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <div className="pt-4 flex justify-end">
              <button
                onClick={() => setCurrentStep(2)}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono uppercase tracking-wider transition-all duration-150 shadow-lg shadow-cyan-500/20"
              >
                <span>Proceed to CORAL Estimation</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="space-y-4">
            <h2 className="text-base font-bold font-mono text-slate-100 flex items-center gap-2">
              <Zap className="w-5 h-5 text-emerald-400" />
              <span>Step 2: Second-Order Covariance Matrix Estimation (CORAL)</span>
            </h2>

            <p className="text-xs text-slate-300 font-mono leading-relaxed">
              CORAL estimates second-order statistics \(C_S\) (Source) and \(C_T\) (Target) on unlabelled flows, computing alignment matrix \(A = C_S^{-1/2} C_T^{1/2}\).
            </p>

            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400">Target Domain:</span>
                <span className="text-cyan-300 font-bold">{targetDomain}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Adaptation Window:</span>
                <span className="text-slate-200">{adaptSize} flows</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Covariance Alignment Matrix:</span>
                <span className="text-emerald-400 font-bold">READY TO FIT</span>
              </div>
            </div>

            <div className="pt-4 flex justify-between">
              <button
                onClick={() => setCurrentStep(1)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono"
              >
                Back
              </button>
              <button
                onClick={() => setCurrentStep(3)}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono uppercase tracking-wider transition-all duration-150"
              >
                <span>Proceed to Calibration</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-4">
            <h2 className="text-base font-bold font-mono text-slate-100 flex items-center gap-2">
              <Sliders className="w-5 h-5 text-amber-400" />
              <span>Step 3: Decision Threshold Calibration Sweep</span>
            </h2>

            <p className="text-xs text-slate-300 font-mono leading-relaxed">
              Sweeps decision threshold \(\tau \in [0.10, 0.90]\) on calibration window ({calibSize} flows) to select argmax MCC threshold.
            </p>

            <div className="pt-4 flex justify-between">
              <button
                onClick={() => setCurrentStep(2)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono"
              >
                Back
              </button>
              <button
                onClick={() => setCurrentStep(4)}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono uppercase tracking-wider transition-all duration-150"
              >
                <span>Proceed to Freeze Threshold</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {currentStep === 4 && (
          <div className="space-y-4">
            <h2 className="text-base font-bold font-mono text-slate-100 flex items-center gap-2">
              <Lock className="w-5 h-5 text-cyan-400" />
              <span>Step 4: Execute Onboarding & Freeze Decision Threshold</span>
            </h2>

            <p className="text-xs text-slate-300 font-mono leading-relaxed">
              Lock the calibrated threshold \(\tau^*\) and verify model performance on the zero-leakage holdout test window.
            </p>

            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400">Target Domain:</span>
                <span className="text-cyan-300 font-bold">{targetDomain}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Adaptation Flows:</span>
                <span className="text-slate-200">{adaptSize}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Calibration Flows:</span>
                <span className="text-slate-200">{calibSize}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Test Flows:</span>
                <span className="text-slate-200">{testSize}</span>
              </div>
            </div>

            <div className="pt-4 flex justify-between">
              <button
                onClick={() => setCurrentStep(3)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono"
              >
                Back
              </button>
              <button
                onClick={handleRunOnboarding}
                disabled={onboardMutation.isPending}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-xs font-mono uppercase tracking-wider transition-all duration-150 shadow-lg shadow-emerald-500/20 disabled:opacity-50"
              >
                <Zap className="w-4 h-4" />
                <span>{onboardMutation.isPending ? 'Executing Onboarding...' : 'Execute Onboarding Simulation'}</span>
              </button>
            </div>
          </div>
        )}

        {currentStep === 5 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold font-mono text-slate-100 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <span>Onboarding Simulation Results & Verified Metrics</span>
              </h2>

              <ProvenanceBadge
                sourceFile="data/samples/nfton.parquet"
                protocolStatus="demo-scale"
              />
            </div>

            {onboardResult ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-xs">
                    <span className="text-slate-400 block text-[10px]">Frozen Threshold (\(\tau\))</span>
                    <span className="text-cyan-400 text-lg font-extrabold">
                      {onboardResult.selected_threshold.toFixed(2)}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-xs">
                    <span className="text-slate-400 block text-[10px]">Holdout Test MCC</span>
                    <span className="text-emerald-400 text-lg font-extrabold">
                      {onboardResult.metrics.mcc.toFixed(4)}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-xs">
                    <span className="text-slate-400 block text-[10px]">F1 Score</span>
                    <span className="text-slate-200 text-lg font-extrabold">
                      {onboardResult.metrics.f1_score.toFixed(4)}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-xs">
                    <span className="text-slate-400 block text-[10px]">False Positive Rate</span>
                    <span className="text-rose-400 text-lg font-extrabold">
                      {onboardResult.metrics.fpr.toFixed(4)}
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs font-mono text-slate-400 flex justify-between">
                  <span>Evaluated Test Window: {onboardResult.evaluated_test_size} flows</span>
                  <span className="text-cyan-400 font-bold">CORAL Fitted: YES</span>
                </div>
              </div>
            ) : (
              <div className="p-6 text-center text-slate-400 font-mono text-xs">
                Click "Execute Onboarding Simulation" in Step 4 to compute target calibration metrics.
              </div>
            )}

            <div className="pt-4 flex justify-between border-t border-slate-800">
              <button
                onClick={() => setCurrentStep(1)}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Restart Wizard</span>
              </button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
