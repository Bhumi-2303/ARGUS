with open("web/src/features/onboard/OnboardingWizardPage.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "import { useMutation } from '@tanstack/react-query';",
    "import { useMutation, useQuery } from '@tanstack/react-query';"
)

content = content.replace(
    "import { api, OnboardResponse } from '../../api/client';",
    "import { api, OnboardResponse, DomainInfo } from '../../api/client';"
)

with open("web/src/features/onboard/OnboardingWizardPage.tsx", "w") as f:
    f.write(content)
