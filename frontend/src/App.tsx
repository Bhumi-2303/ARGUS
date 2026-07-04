
import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
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
            <Route path="/agents" element={<div className="p-4">Agent Management</div>} />
            <Route path="/threats" element={<div className="p-4">Threat Intel</div>} />
            <Route path="/network" element={<div className="p-4">Network Graph</div>} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
