import re

with open("web/src/components/MetricTile.tsx", "r") as f:
    code = f.read()

code = code.replace('text-slate-100', 'text-slate-900 dark:text-slate-100')
code = code.replace('text-slate-400', 'text-slate-500 dark:text-slate-400')
code = code.replace('bg-slate-800/80 text-cyan-400 border border-slate-700/50', 'bg-slate-100 dark:bg-slate-800/80 text-cyan-600 dark:text-cyan-400 border border-slate-200 dark:border-slate-700/50')
code = code.replace('border-slate-800/80', 'border-slate-200 dark:border-slate-800/80')
code = code.replace('bg-slate-800', 'bg-slate-200 dark:bg-slate-800')

with open("web/src/components/MetricTile.tsx", "w") as f:
    f.write(code)
