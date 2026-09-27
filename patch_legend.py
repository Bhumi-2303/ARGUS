import re
with open("web/src/features/monitor/LiveMonitorPage.tsx", "r") as f:
    content = f.read()

# Add a tiny HTML legend before the ECharts ReactECharts component
chart_div_regex = r"(<div className=\"h-\[350px\] w-full\">\s*<ReactECharts)"
replacement = """<div className="flex justify-end px-4 mb-2">
          <div className="flex items-center gap-2 text-[10px] font-mono text-slate-500 dark:text-slate-400">
            <div className="w-3 h-3 rounded-sm bg-rose-500/15 border border-rose-500/30"></div>
            <span>Shaded areas indicate true Attack flows</span>
          </div>
        </div>
        \\1"""

content = re.sub(chart_div_regex, replacement, content)

with open("web/src/features/monitor/LiveMonitorPage.tsx", "w") as f:
    f.write(content)
