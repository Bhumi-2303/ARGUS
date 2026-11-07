import re
with open("web/src/features/benchmark/ModelComparisonPage.tsx", "r") as f:
    content = f.read()

# Make sure ModelStatusBadge is imported
if "ModelStatusBadge" not in content:
    content = "import { ModelStatusBadge } from '../../components/ModelStatusBadge';\n" + content

# Add modelInfo to mapped object
content = re.sub(
    r"protocol_status: matchedModel\?\.protocol_status \|\| r\.Protocol_Status \|\| \(r\.Model\?\.includes\('DANN'\) \? 'dann_adapted' : 'final'\),\s*};",
    r"protocol_status: matchedModel?.protocol_status || r.Protocol_Status || (r.Model?.includes('DANN') ? 'dann_adapted' : 'final'),\n      modelInfo: matchedModel,\n    };",
    content
)

# Table row replacement
content = re.sub(
    r'(<td className="p-3 font-bold flex items-center gap-2">.*?<div className="flex items-center gap-1.5">\s*<Network className="w-4 h-4 text-slate-500" />\s*<span className="truncate">\{r\.model_name\}</span>\s*</div>\s*</td>)',
    r'<td className="p-3 font-bold flex items-center justify-between gap-2">\n                            <div className="flex items-center gap-1.5">\n                              <Network className="w-4 h-4 text-slate-500" />\n                              <span className="truncate">{r.model_name}</span>\n                            </div>\n                            {r.modelInfo && <ModelStatusBadge status={r.modelInfo.status} />}\n                          </td>',
    content,
    flags=re.DOTALL
)

# Mobile card replacement
content = re.sub(
    r'(<div className="flex justify-between items-center text-cyan-300 font-bold border-b border-slate-800/80 pb-2 mb-2">\s*<span className="truncate">\{r\.model_name\}</span>)',
    r'\1\n                    {r.modelInfo && <ModelStatusBadge status={r.modelInfo.status} />}',
    content
)

with open("web/src/features/benchmark/ModelComparisonPage.tsx", "w") as f:
    f.write(content)
