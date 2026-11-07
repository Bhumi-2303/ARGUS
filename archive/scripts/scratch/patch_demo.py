path = "web/src/features/demo/InteractiveDemoPage.tsx"
with open(path, "r") as f:
    code = f.read()

code = code.replace("""<StatusPill status={result.prediction === 1 ? 'error' : 'healthy'} label={result.prediction === 1 ? 'ATTACK' : 'BENIGN'} />""", 
                    """<StatusPill status={result.prediction === 1 ? 'error' : result.prediction === 0 ? 'healthy' : 'warning'} label={result.prediction === 1 ? 'ATTACK' : result.prediction === 0 ? 'BENIGN' : 'UNKNOWN'} />""")

code = code.replace("""className={`h-2 rounded-full ${result.prediction === 1 ? 'bg-red-500' : 'bg-emerald-500'}`}""", 
                    """className={`h-2 rounded-full ${result.prediction === 1 ? 'bg-red-500' : result.prediction === 0 ? 'bg-emerald-500' : 'bg-slate-500'}` }""")

with open(path, "w") as f:
    f.write(code)
