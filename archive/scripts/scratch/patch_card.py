import re

with open("web/src/components/Card.tsx", "r") as f:
    code = f.read()

# Make it completely solid and restrained, matching standard UI.
code = code.replace("rounded-xl", "rounded-md")
code = code.replace("bg-slate-900/80 dark:bg-slate-900/80 border border-slate-800 shadow-xl shadow-slate-950/20 text-slate-100", 
                    "bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100")
code = code.replace("glass-panel text-slate-100 shadow-xl shadow-cyan-950/10", "bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800")
code = code.replace("bg-transparent border border-slate-800 text-slate-100", "bg-transparent border border-slate-200 dark:border-slate-800")
code = code.replace("bg-gradient-to-br from-slate-900 via-slate-900 to-cyan-950/40 border border-cyan-500/20 text-slate-100 shadow-lg shadow-cyan-950/30", 
                    "bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800")

# Adjust header text styles
code = code.replace("text-slate-100", "text-slate-900 dark:text-slate-100")
code = code.replace("text-slate-400", "text-slate-500 dark:text-slate-400")
code = code.replace("border-slate-800/80", "border-slate-200 dark:border-slate-800")

with open("web/src/components/Card.tsx", "w") as f:
    f.write(code)
