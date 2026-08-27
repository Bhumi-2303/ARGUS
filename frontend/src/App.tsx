import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Pipeline from './pages/Pipeline'
import AgentDetails from './pages/AgentDetails'
import ModelEvaluation from './pages/ModelEvaluation'
import Sidebar from './components/layout/Sidebar'
import Topbar from './components/layout/Topbar'

function App() {
  return (
    <div className="flex h-screen bg-slate-950 text-slate-50 overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-950/50 p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/pipeline/:agentId" element={<AgentDetails />} />
            <Route path="/models" element={<ModelEvaluation />} />
            <Route path="/agents" element={<div className="p-4">Agent Management</div>} />
            <Route path="/threats" element={<div className="p-4">Threat Intel</div>} />
            <Route path="/network" element={<div className="p-4">Network Graph</div>} />
            <Route path="/alerts/:id" element={<div className="p-4">Alert Details</div>} />
            <Route path="/reports" element={<div className="p-4">Reports & Logs</div>} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
