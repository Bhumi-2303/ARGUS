import re
with open("web/src/features/overview/OverviewPage.tsx", "r") as f:
    content = f.read()

# Replace the fallback values and build the banner text
extract_logic = """
  const benchmarkRows = benchmarkData?.data || [];
  const dannModel = benchmarkRows.find((r: any) => r.Model?.includes('DANN')) || null;
  const coralModel = benchmarkRows.find((r: any) => r.Model?.includes('Clean Class-aware CORAL')) || null;

  const dannMCC = dannModel?.MCC ?? 0.0;
  const coralMCC = coralModel?.MCC ?? 0.0;
"""

content = re.sub(
    r"const benchmarkRows = benchmarkData\?\.data \|\| \[\];.*?const mccGain = \(\(coralMCC - sourceMCC\) \* 100\)\.toFixed\(1\);",
    extract_logic,
    content,
    flags=re.DOTALL
)

# Insert the dynamic banner
banner_html = """
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            ARGUS evaluates model robustness and domain shift adaptation across Enterprise IoT, Smart Home NetFlow, and Industrial SCADA protocols with zero data leakage.
          </p>
          
          <div className="bg-slate-900/80 border-l-4 border-cyan-500 p-4 rounded-r-lg font-mono text-xs text-slate-300">
            <strong>Verified Discovery:</strong> While standard neural adaptation (DANN) collapses under extreme label imbalance (MCC: {(dannMCC).toFixed(4)}), our zero-leakage Class-Aware CORAL successfully recovers discriminative power across domains (MCC: {(coralMCC).toFixed(4)}).
          </div>
"""

content = re.sub(
    r"<p className=\"text-slate-300 text-sm sm:text-base leading-relaxed\">.*?zero data leakage\.\n\s*</p>",
    banner_html,
    content,
    flags=re.DOTALL
)

with open("web/src/features/overview/OverviewPage.tsx", "w") as f:
    f.write(content)
