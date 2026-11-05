import re

with open("web/src/features/overview/OverviewPage.tsx", "r") as f:
    code = f.read()

code = code.replace("ARGUS Domain Adaptation & Telemetry", "1. System / Project Overview")
code = code.replace("Key evaluation metrics, model generalization", "System narrative, core empirical findings, adaptation impact, and platform capabilities")

with open("web/src/features/overview/OverviewPage.tsx", "w") as f:
    f.write(code)
