with open("web/src/features/demo/InteractiveDemoPage.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "import { apiClient } from '../../api/client';",
    "import { api } from '../../api/client';"
)

content = content.replace(
    "const res = await apiClient.post('/predict', {",
    "const res = await api.predict({"
)

# Replace .data with direct return from fetchJson
content = content.replace(
    "setResult(res.data);",
    "setResult(res);"
)
content = content.replace(
    "setErrorMsg(err.response?.data?.detail || err.message || 'Unknown error during inference');",
    "setErrorMsg(err.message || 'Unknown error during inference');"
)


content = content.replace(
    "<StatusPill status={result.prediction === 1 ? 'critical' : 'healthy'}>\n                    {result.prediction === 1 ? 'ATTACK' : 'BENIGN'}\n                  </StatusPill>",
    "<StatusPill status={result.prediction === 1 ? 'error' : 'healthy'} label={result.prediction === 1 ? 'ATTACK' : 'BENIGN'} />"
)

with open("web/src/features/demo/InteractiveDemoPage.tsx", "w") as f:
    f.write(content)
