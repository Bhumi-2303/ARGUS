import re

def patch_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    # Import the icon if not present
    if "MetricInfoIcon" not in content:
        content = "import { MetricInfoIcon } from '../../components/MetricInfoIcon';\n" + content

    # Replace specific metric labels with the icon appended
    # LiveMonitorPage
    content = re.sub(
        r'<span className="text-slate-400">Balanced Acc:</span>',
        r'<span className="text-slate-400 flex items-center">Balanced Acc: <MetricInfoIcon metric="balanced_acc" /></span>',
        content
    )
    content = re.sub(
        r'<span className="text-slate-400">Specificity:</span>',
        r'<span className="text-slate-400 flex items-center">Specificity: <MetricInfoIcon metric="specificity" /></span>',
        content
    )
    content = re.sub(
        r'<span className="text-slate-400">Recall:</span>',
        r'<span className="text-slate-400 flex items-center">Recall: <MetricInfoIcon metric="recall" /></span>',
        content
    )

    # ModelComparisonPage table headers
    content = re.sub(
        r'<th className="p-3">Balanced Acc</th>',
        r'<th className="p-3"><div className="flex items-center gap-1">Balanced Acc <MetricInfoIcon metric="balanced_acc" /></div></th>',
        content
    )
    content = re.sub(
        r'<th className="p-3">Specificity</th>',
        r'<th className="p-3"><div className="flex items-center gap-1">Specificity <MetricInfoIcon metric="specificity" /></div></th>',
        content
    )
    content = re.sub(
        r'<th className="p-3">Recall</th>',
        r'<th className="p-3"><div className="flex items-center gap-1">Recall <MetricInfoIcon metric="recall" /></div></th>',
        content
    )

    with open(filepath, "w") as f:
        f.write(content)

patch_file("web/src/features/monitor/LiveMonitorPage.tsx")
patch_file("web/src/features/benchmark/ModelComparisonPage.tsx")
