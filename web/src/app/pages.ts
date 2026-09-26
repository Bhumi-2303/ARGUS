import React, { lazy } from 'react';
import {
  LayoutDashboard,
  Activity,
  GitBranch,
  BarChart3,
  Search,
  PlusCircle,
  FileCheck2,
  Cpu,
  LucideIcon,
} from 'lucide-react';


export interface PageDefinition {
  id: string;
  path: string;
  title: string;
  description: string;
  category: 'Overview' | 'Evaluation & Verification' | 'Domain Adaptation';
  icon: LucideIcon;
  component: React.LazyExoticComponent<React.ComponentType<any>> | React.ComponentType<any>;
  badge?: string;
}

// Lazy loaded page components for all 7 pages
const OverviewPage = lazy(() => import('../features/overview/OverviewPage'));
const LiveMonitorPage = lazy(() => import('../features/monitor/LiveMonitorPage'));
const DomainShiftPage = lazy(() => import('../features/shift/DomainShiftPage'));
const ModelComparisonPage = lazy(() => import('../features/benchmark/ModelComparisonPage'));
const ExplainabilityPage = lazy(() => import('../features/explain/ExplainabilityPage'));
const OnboardingWizardPage = lazy(() => import('../features/onboard/OnboardingWizardPage'));
const ProtocolLimitsPage = lazy(() => import('../features/protocol_limits/ProtocolLimitsPage'));
const TopologyPage = lazy(() => import('../features/topology/TopologyPage'));

export const PAGES: PageDefinition[] = [
  {
    id: 'overview',
    path: '/',
    title: 'Overview',
    description: 'System narrative, core empirical findings, adaptation impact, and platform limitations.',
    category: 'Overview',
    icon: LayoutDashboard,
    component: OverviewPage,
    badge: 'START',
  },
  {
    id: 'monitor',
    path: '/monitor',
    title: 'Live Monitor',
    description: 'Real-time telemetry flow stream, balanced accuracy tracking, and domain shift detection.',
    category: 'Overview',
    icon: Activity,
    component: LiveMonitorPage,
    badge: 'LIVE',
  },
  {
    id: 'topology',
    path: '/topology',
    title: 'System Topology',
    description: 'Dynamic 3D/2D agent graph visualization, websocket live status, and flow event tracing.',
    category: 'Overview',
    icon: Cpu,
    component: TopologyPage,
    badge: '3D',
  },
  {
    id: 'shift',
    path: '/shift',
    title: 'Domain Shift',
    description: 'KS-test feature distribution shifts, PSI drift scores, and domain classifier metrics.',
    category: 'Domain Adaptation',
    icon: GitBranch,
    component: DomainShiftPage,
  },
  {
    id: 'benchmark',
    path: '/benchmark',
    title: 'Model Comparison',
    description: 'Verified side-by-side performance tables, radar charts, and diagnostic runs.',
    category: 'Evaluation & Verification',
    icon: BarChart3,
    component: ModelComparisonPage,
  },
  {
    id: 'explain',
    path: '/explain',
    title: 'Explainability',
    description: 'SHAP feature attributions, waterfall impact breakdown, and gain rank comparison.',
    category: 'Evaluation & Verification',
    icon: Search,
    component: ExplainabilityPage,
  },
  {
    id: 'onboard',
    path: '/onboard',
    title: 'Onboard a Network',
    description: 'Demo-scale step-by-step target domain CORAL alignment and threshold calibration wizard.',
    category: 'Domain Adaptation',
    icon: PlusCircle,
    component: OnboardingWizardPage,
    badge: 'DEMO',
  },
  {
    id: 'protocol-limits',
    path: '/protocol-limits',
    title: 'Protocol & Limits',
    description: 'Zero-leakage split controls, single-seed disclosures, prior shift, and known caveats.',
    category: 'Evaluation & Verification',
    icon: FileCheck2,
    component: ProtocolLimitsPage,
  },
];

