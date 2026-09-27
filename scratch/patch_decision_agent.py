import re

with open("src/argus/services/decision_agent/main.py", "r") as f:
    code = f.read()

# Replace hardcoded fallback 74.19 with explicit exception or "Unknown" string, but wait, the f-string formats it as .2f!
# We can just change it to raise an error or use "Unknown" and remove the .2f if None.
code = code.replace(
    "{risk_score if risk_score is not None else 74.19:.2f}",
    "{f'{risk_score:.2f}' if risk_score is not None else 'Unknown'}"
)

with open("src/argus/services/decision_agent/main.py", "w") as f:
    f.write(code)
