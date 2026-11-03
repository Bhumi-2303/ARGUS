import re
with open("web/src/features/monitor/LiveMonitorPage.tsx", "r") as f:
    content = f.read()

# Add to legend
content = re.sub(
    r"legend: \{\s*data: selectedModels,",
    "legend: {\n      data: ['Ground Truth (Attack)', ...selectedModels],",
    content
)

# Replace series logic
old_series = """    series: selectedModels.map((mId) => ({
      name: mId,
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: [...flowHistory]
        .reverse()
        .map((f) => f.predictions[mId]?.probability ?? 0),
    })),"""

new_series = """    series: [
      {
        name: 'Ground Truth (Attack)',
        type: 'line',
        step: 'middle',
        symbol: 'none',
        lineStyle: { width: 0 },
        areaStyle: { color: 'rgba(244, 63, 94, 0.15)' }, // Rose-500 with low opacity
        data: [...flowHistory].reverse().map((f) => f.true_label),
        z: 0,
      },
      ...selectedModels.map((mId) => ({
        name: mId,
        type: 'line',
        smooth: true,
        showSymbol: false,
        data: [...flowHistory]
          .reverse()
          .map((f) => f.predictions[mId]?.probability ?? 0),
        z: 10,
      }))
    ],"""

content = content.replace(old_series, new_series)

# Update tooltip
old_tooltip = """    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      textStyle: { color: '#f8fafc', fontSize: 11, fontFamily: 'monospace' },
    },"""

new_tooltip = """    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      textStyle: { color: '#f8fafc', fontSize: 11, fontFamily: 'monospace' },
      formatter: function (params: any) {
        if (!params || !params.length) return '';
        const axisValue = params[0].axisValue;
        let html = `<div class="font-bold border-b border-slate-700 pb-1 mb-1">Flow ID: ${axisValue}</div>`;
        
        let trueLabel = 0;
        const gtParam = params.find((p: any) => p.seriesName === 'Ground Truth (Attack)');
        if (gtParam) {
          trueLabel = gtParam.value;
          html += `<div class="mb-2">Ground Truth: ${trueLabel === 1 ? '<span style="color:#fb7185">ATTACK</span>' : '<span style="color:#34d399">BENIGN</span>'}</div>`;
        }

        params.forEach((p: any) => {
          if (p.seriesName === 'Ground Truth (Attack)') return;
          const prob = p.value;
          const predClass = prob >= 0.5 ? 1 : 0;
          const isCorrect = predClass === trueLabel;
          const color = p.color;
          const correctMark = isCorrect ? '✅' : '❌';
          
          html += `<div style="display:flex; justify-content:space-between; gap:12px; margin-top:4px;">
            <span style="color:${color}">${p.seriesName}</span>
            <span>
              ${(prob * 100).toFixed(1)}% 
              (${predClass === 1 ? 'ATK' : 'BEN'}) 
              ${correctMark}
            </span>
          </div>`;
        });
        return html;
      }
    },"""

content = content.replace(old_tooltip, new_tooltip)

with open("web/src/features/monitor/LiveMonitorPage.tsx", "w") as f:
    f.write(content)
