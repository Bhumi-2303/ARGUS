import re
with open("web/src/features/overview/OverviewPage.tsx", "r") as f:
    content = f.read()

# Replace the "Start Monitoring" button area
old_btn = """            <Link
              to="/monitor"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs uppercase tracking-wider transition-all duration-200 shadow-lg shadow-cyan-500/25 focus:ring-2 focus:ring-cyan-400 focus:outline-none"
            >
              <Activity className="w-4 h-4" />
              Start Monitoring
            </Link>"""

new_btns = """            <Link
              to="/monitor"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs uppercase tracking-wider transition-all duration-200 shadow-lg shadow-cyan-500/25 focus:ring-2 focus:ring-cyan-400 focus:outline-none"
            >
              <Activity className="w-4 h-4" />
              Live Monitor
            </Link>
            <Link
              to="/judge-mode"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-slate-50 font-bold text-xs uppercase tracking-wider transition-all duration-200 shadow-lg shadow-indigo-600/25 border border-indigo-500 focus:ring-2 focus:ring-indigo-400 focus:outline-none"
            >
              <Play className="w-4 h-4" />
              Start Judge Mode
            </Link>"""

content = content.replace(old_btn, new_btns)

# Also ensure Play is imported
if "Play" not in content:
    content = content.replace("import { ShieldCheck, Activity,", "import { ShieldCheck, Activity, Play,")

with open("web/src/features/overview/OverviewPage.tsx", "w") as f:
    f.write(content)
