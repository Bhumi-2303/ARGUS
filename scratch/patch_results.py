import re

with open("web/src/features/results/ResultsPage.tsx", "r") as f:
    code = f.read()

code = code.replace("5. Results & Evaluation Overview", "6. Results & Evaluation Overview")

with open("web/src/features/results/ResultsPage.tsx", "w") as f:
    f.write(code)
