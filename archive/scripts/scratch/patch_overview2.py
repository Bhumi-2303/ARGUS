import re

with open("web/src/features/overview/OverviewPage.tsx", "r") as f:
    code = f.read()

code = code.replace("rounded-2xl bg-gradient-to-r from-slate-900 via-slate-800 to-cyan-950 border border-slate-800 p-8 shadow-2xl", 
                    "rounded-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8")

with open("web/src/features/overview/OverviewPage.tsx", "w") as f:
    f.write(code)
