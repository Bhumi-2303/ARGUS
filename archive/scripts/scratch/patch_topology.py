import re

with open("web/src/features/topology/TopologyPage.tsx", "r") as f:
    code = f.read()

# Fix button styling
code = code.replace("rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-extrabold text-xs font-mono uppercase tracking-wider transition-all duration-150 shadow-lg shadow-cyan-500/20", 
                    "rounded bg-cyan-600 hover:bg-cyan-700 text-white font-medium text-xs font-mono uppercase tracking-wider transition-colors")

# Remove blur
code = code.replace("backdrop-blur", "")

with open("web/src/features/topology/TopologyPage.tsx", "w") as f:
    f.write(code)
