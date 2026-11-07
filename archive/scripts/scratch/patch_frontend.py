import os

# 1. OverviewPage.tsx
path = "web/src/features/overview/OverviewPage.tsx"
with open(path, "r") as f:
    code = f.read()
# Replace: {shiftData?.domain_shift ? (...) : (...)}
code = code.replace("""{shiftData?.domain_shift ? (
                    <span className="text-rose-400 font-bold flex items-center gap-1 text-xs mt-1">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      DRIFT DETECTED
                    </span>
                  ) : (
                    <span className="text-emerald-400 font-bold flex items-center gap-1 text-xs mt-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      STABLE
                    </span>
                  )}""", """{shiftData?.domain_shift === true ? (
                    <span className="text-rose-400 font-bold flex items-center gap-1 text-xs mt-1">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      DRIFT DETECTED
                    </span>
                  ) : shiftData?.domain_shift === false ? (
                    <span className="text-emerald-400 font-bold flex items-center gap-1 text-xs mt-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      STABLE
                    </span>
                  ) : (
                    <span className="text-slate-400 font-bold flex items-center gap-1 text-xs mt-1">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      ERROR LOADING
                    </span>
                  )}""")
with open(path, "w") as f:
    f.write(code)


# 2. DomainShiftPage.tsx
path = "web/src/features/shift/DomainShiftPage.tsx"
with open(path, "r") as f:
    code = f.read()

code = code.replace("""{shiftData?.domain_shift ? (
                  <span className="text-rose-400 font-extrabold flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" /> DRIFT DETECTED
                  </span>
                ) : (
                  <span className="text-emerald-400 font-extrabold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> STABLE
                  </span>
                )}""", """{shiftData?.domain_shift === true ? (
                  <span className="text-rose-400 font-extrabold flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" /> DRIFT DETECTED
                  </span>
                ) : shiftData?.domain_shift === false ? (
                  <span className="text-emerald-400 font-extrabold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> STABLE
                  </span>
                ) : (
                  <span className="text-slate-400 font-extrabold flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" /> ERROR LOADING
                  </span>
                )}""")
with open(path, "w") as f:
    f.write(code)

