import re

with open("web/src/components/Sidebar.tsx", "r") as f:
    code = f.read()

code = code.replace("bg-gradient-to-tr from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/20 shrink-0", 
                    "bg-blue-600 text-white shrink-0")
code = code.replace("rounded-xl", "rounded")

with open("web/src/components/Sidebar.tsx", "w") as f:
    f.write(code)
