import re
with open("web/src/features/system_overview/SystemOverviewPage.tsx", "r") as f:
    content = f.read()

if "ModelStatusBadge" not in content:
    content = "import { ModelStatusBadge } from '../../components/ModelStatusBadge';\n" + content

# Patch StatusPill line
content = re.sub(
    r'<StatusPill status=\{m\.protocol_status\} pulse=\{false\} />',
    r'<ModelStatusBadge status={m.status} />',
    content
)

with open("web/src/features/system_overview/SystemOverviewPage.tsx", "w") as f:
    f.write(content)
