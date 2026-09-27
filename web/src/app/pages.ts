import React, { lazy } from 'react';
import {
  LayoutDashboard,
  Database,
  Cpu,
  Search,
  BarChart3,
  LucideIcon
} from 'lucide-react';

export interface PageDefinition {
  id: string;
  path: string;
  title: string;
  description: string;
  category: string;
  icon: LucideIcon;
  component: React.LazyExoticComponent<React.ComponentType<any>> | React.ComponentType<any>;
  badge?: string;
}

const OverviewPage = lazy(() => import('../features/overview/OverviewPage'));
const InputAnalysisPage = lazy(() => import('../features/analysis/InputAnalysisPage'));
const TopologyPage = lazy(() => import('../features/topology/TopologyPage'));
const ExplainabilityPage = lazy(() => import('../features/explain/ExplainabilityPage'));
const ResultsPage = lazy(() => import('../features/results/ResultsPage'));

export const PAGES: PageDefinition[] = [
  {
    id: 'overview',
    path: '/',
    title: 'System Overview',
    description: 'System narrative, core empirical findings, adaptation impact, and platform limitations.',
    category: 'Navigation',
    icon: LayoutDashboard,
    component: OverviewPage,
  },
  {
    id: 'input',
    path: '/input',
    title: 'Input & Prediction',
    description: 'Select actual network flow samples and run the real ARGUS pipeline.',
    category: 'Navigation',
    icon: Database,
    component: InputAnalysisPage,
    badge: 'LIVE',
  },
  {
    id: 'topology',
    path: '/topology',
    title: 'Multi-Agent Processing',
    description: 'Dynamic visualization of the agent graph and live flow execution tracing.',
    category: 'Navigation',
    icon: Cpu,
    component: TopologyPage,
  },
  {
    id: 'explain',
    path: '/explain',
    title: 'Explanation & Visualization',
    description: 'Actual SHAP feature attributions and target gain disconnected visualizations.',
    category: 'Navigation',
    icon: Search,
    component: ExplainabilityPage,
  },
  {
    id: 'results',
    path: '/results',
    title: 'Results & Evaluation',
    description: 'Verified side-by-side performance tables, domain shift, and evaluation metrics.',
    category: 'Navigation',
    icon: BarChart3,
    component: ResultsPage,
  }
];
