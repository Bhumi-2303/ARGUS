with open("web/src/features/onboard/OnboardingWizardPage.tsx", "r") as f:
    content = f.read()

if "useQuery" not in content:
    content = content.replace("import { useState } from 'react';", "import { useState } from 'react';\nimport { useQuery } from '@tanstack/react-query';")

content = content.replace(
    """  const [targetDomain, setTargetDomain] = useState<string>('nfton');""",
    """  const [targetDomain, setTargetDomain] = useState<string>('nfton');
  const { data: domainsData } = useQuery({ queryKey: ['domains'], queryFn: api.getDomains });
  const domainOptions = domainsData?.domains || [];"""
)

content = content.replace(
    """                  <select
                    id="onboard-domain-select"
                    value={targetDomain}
                    onChange={(e) => setTargetDomain(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
                  >
                    <option value="nfton">NF-ToN-IoT-v2 (Smart Home / Industrial IoT)</option>
                    <option value="iec104">IEC 60870-5-104 (Power Grid SCADA Substation)</option>
                  </select>""",
    """                  <select
                    id="onboard-domain-select"
                    value={targetDomain}
                    onChange={(e) => setTargetDomain(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
                  >
                    {domainOptions.filter(d => d.domain_id !== 'ciciot').map(d => (
                      <option 
                        key={d.domain_id} 
                        value={d.domain_id}
                        disabled={d.status !== 'verified'}
                        title={d.status === 'planned' ? 'Not yet backed by a verified result' : d.status === 'partial' ? 'Partially verified — see Protocol & Limits' : ''}
                      >
                        {d.name} {d.status !== 'verified' ? `(${d.status})` : ''}
                      </option>
                    ))}
                  </select>"""
)

with open("web/src/features/onboard/OnboardingWizardPage.tsx", "w") as f:
    f.write(content)
