import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';

import OverviewPage from './pages/OverviewPage';
import AlertsPage from './pages/AlertsPage';
import AlertDetailPage from './pages/AlertDetailPage';
import NetworkPage from './pages/NetworkPage';
import PipelinePage from './pages/PipelinePage';
import AgentDetailPage from './pages/AgentDetailPage';
import ModelsPage from './pages/ModelsPage';
import ExplainabilityPage from './pages/ExplainabilityPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<OverviewPage />} />
        <Route path="alerts" element={<AlertsPage />} />
        <Route path="alerts/:id" element={<AlertDetailPage />} />
        <Route path="network" element={<NetworkPage />} />
        <Route path="pipeline" element={<PipelinePage />} />
        <Route path="pipeline/:agentId" element={<AgentDetailPage />} />
        <Route path="models" element={<ModelsPage />} />
        <Route path="explainability" element={<ExplainabilityPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
