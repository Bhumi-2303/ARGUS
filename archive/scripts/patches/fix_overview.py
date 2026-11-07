import re
with open("web/src/features/overview/OverviewPage.tsx", "r") as f:
    content = f.read()

# I replaced sourceModel, so let's put it back!
extract_logic = """
  const benchmarkRows = benchmarkData?.data || [];
  const dannModel = benchmarkRows.find((r: any) => r.Model?.includes('DANN')) || null;
  const coralModel = benchmarkRows.find((r: any) => r.Model?.includes('Clean Class-aware CORAL')) || null;
  const sourceModel = benchmarkRows.find((r: any) => r.Model?.includes('Global CORAL')) || null;

  const dannMCC = dannModel?.MCC ?? 0.0;
  const coralMCC = coralModel?.MCC ?? 0.0;
  const sourceMCC = sourceModel?.MCC ?? 0.0;
  
  const mccGain = ((coralMCC - dannMCC) * 100).toFixed(1);
"""

content = re.sub(
    r"const benchmarkRows = benchmarkData\?\.data \|\| \[\];.*?const coralMCC = coralModel\?\.MCC \?\? 0\.0;",
    extract_logic,
    content,
    flags=re.DOTALL
)

# And make sure Play is imported
if "Play" not in content:
    content = content.replace("import { ShieldCheck, Activity,", "import { ShieldCheck, Activity, Play,")

with open("web/src/features/overview/OverviewPage.tsx", "w") as f:
    f.write(content)
