import re

with open("web/src/features/analysis/InputAnalysisPage.tsx", "r") as f:
    code = f.read()

code = code.replace('animate-in fade-in slide-in-from-bottom-4', 'animate-in fade-in')
code = code.replace('rounded-full', 'rounded-sm')

with open("web/src/features/analysis/InputAnalysisPage.tsx", "w") as f:
    f.write(code)
