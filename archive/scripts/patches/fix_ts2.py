with open("web/src/features/onboard/OnboardingWizardPage.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "import { useQuery } from '@tanstack/react-query';",
    "import { useQuery } from '@tanstack/react-query';\nimport { api, DomainInfo } from '../../api/client';"
)

content = content.replace(
    "domainOptions.filter(d => d.domain_id !== 'ciciot')",
    "domainOptions.filter((d: DomainInfo) => d.domain_id !== 'ciciot')"
)
content = content.replace(
    ".map(d => (",
    ".map((d: DomainInfo) => ("
)

with open("web/src/features/onboard/OnboardingWizardPage.tsx", "w") as f:
    f.write(content)
