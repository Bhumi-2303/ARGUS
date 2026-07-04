
import { Bell, Search, User } from 'lucide-react'

export default function Topbar() {
  return (
    <header className="h-16 flex-shrink-0 glass-panel !rounded-none !border-x-0 !border-t-0 flex items-center justify-between px-6 z-10">
      <div className="flex-1 flex items-center">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search alerts, agents..." 
            className="w-full bg-slate-900/50 border border-slate-700 rounded-lg pl-10 pr-4 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500/50 text-slate-200"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs text-slate-400 font-medium">System Online</span>
        </div>
        
        <button className="relative p-2 text-slate-400 hover:text-slate-100 transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-500 border border-slate-950" />
        </button>
        
        <div className="h-8 w-8 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700 cursor-pointer">
          <User className="w-4 h-4 text-slate-400" />
        </div>
      </div>
    </header>
  )
}
