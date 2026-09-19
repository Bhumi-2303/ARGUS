import { Routes, Route } from 'react-router-dom'
import CommandCenter from './pages/CommandCenter'
import IncidentInvestigation from './pages/IncidentInvestigation'
import AssetIntelligence from './pages/AssetIntelligence'
import Analytics from './pages/Analytics'
import SystemHealthView from './pages/SystemHealth'
import { Sidebar } from './components/layout/Sidebar'
import Topbar from './components/layout/Topbar'

import { AlertsPage } from './pages/AlertsPage'
import { AlertDetailPage } from './pages/AlertDetailPage'
import { NetworkPage } from './pages/NetworkPage'
import { ExplainabilityPage } from './pages/ExplainabilityPage'
import { ReportsPage } from './pages/ReportsPage'


function App() {
  return (
    <div className="flex h-screen bg-slate-950 text-slate-50 overflow-hidden font-sans">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-950/50 p-6">
          <Routes>
            <Route path="/" element={<CommandCenter />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/alerts/:id" element={<AlertDetailPage />} />
            <Route path="/incidents/:id" element={<IncidentInvestigation />} />
            <Route path="/assets" element={<AssetIntelligence />} />
            <Route path="/network" element={<NetworkPage />} />
            <Route path="/explainability" element={<ExplainabilityPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/health" element={<SystemHealthView />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
