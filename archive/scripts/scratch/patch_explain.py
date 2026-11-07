import re

with open("web/src/features/explain/ExplainabilityPage.tsx", "r") as f:
    code = f.read()

code = code.replace("Model Explainability & Target Gain", "5. Explanation & Visualization")

with open("web/src/features/explain/ExplainabilityPage.tsx", "w") as f:
    f.write(code)
