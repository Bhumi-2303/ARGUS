import re
with open("web/src/components/ProvenanceBadge.tsx", "r") as f:
    content = f.read()

content = content.replace("'requires verification';", "'requires verification'\n  | 'planned';")

new_status_config = """    'requires verification': {
      label: 'Needs Verification',
      bg: 'bg-rose-500/10',
      text: 'text-rose-400',
      border: 'border-rose-500/30',
      icon: <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />,
    },
    'planned': {
      label: 'Planned',
      bg: 'bg-slate-500/10',
      text: 'text-slate-400',
      border: 'border-slate-500/30',
      icon: <Info className="w-3.5 h-3.5 text-slate-400" />,
    },"""

content = re.sub(r"'requires verification': \{.*?\},", new_status_config, content, flags=re.DOTALL)

with open("web/src/components/ProvenanceBadge.tsx", "w") as f:
    f.write(content)
