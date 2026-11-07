import re
with open("web/src/features/monitor/LiveMonitorPage.tsx", "r") as f:
    content = f.read()

# Make sure ModelStatusBadge is imported
if "ModelStatusBadge" not in content:
    content = "import { ModelStatusBadge } from '../../components/ModelStatusBadge';\n" + content

# In LiveMonitorPage, find the model header:
# <h3 className="text-sm font-bold font-mono text-slate-100 flex items-center gap-2">
#   <Server className="w-4 h-4 text-cyan-400" />
#   <span>{modelInfo?.name || mId}</span>
# </h3>

header_pattern = r'(<h3 className="text-sm font-bold font-mono text-slate-100 flex items-center gap-2">\s*<Server className="w-4 h-4 text-cyan-400" />\s*<span>\{modelInfo\?\.name \|\| mId\}</span>\s*</h3>)'
replacement = r'\1\n              {modelInfo && <ModelStatusBadge status={modelInfo.status} />}'

content = re.sub(header_pattern, replacement, content)

with open("web/src/features/monitor/LiveMonitorPage.tsx", "w") as f:
    f.write(content)
