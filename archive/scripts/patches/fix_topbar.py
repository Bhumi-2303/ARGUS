with open("web/src/components/TopBar.tsx", "r") as f:
    content = f.read()

# Add imports
content = content.replace(
    "import { clsx } from 'clsx';",
    "import { clsx } from 'clsx';\nimport { useQuery } from '@tanstack/react-query';\nimport { api, DomainInfo } from '../api/client';"
)

# Remove hardcoded DOMAINS
content = content.replace(
    """export const DOMAINS = [
  { id: 'ciciot', name: 'Domain 1: CICIoT2023', subtitle: 'Source IoT Telemetry (5.49M)' },
  { id: 'nfton', name: 'Domain 2: NF-ToN-IoT-v2', subtitle: 'Target IoT Telemetry (8.41M)' },
  { id: 'iec104', name: 'Domain 3: IEC-104 SCADA', subtitle: 'Industrial Grid Protocol (2.29M)' },
];""",
    ""
)

# Insert logic inside TopBar component
logic = """  const { data: domainsData } = useQuery({
    queryKey: ['domains'],
    queryFn: api.getDomains,
  });
  const domains = domainsData?.domains || [];
  const activeDomain = domains.find((d) => d.domain_id === selectedDomain) || domains[0] || { name: 'Loading...' };
"""

content = content.replace(
    "  const activeDomain = DOMAINS.find((d) => d.id === selectedDomain) || DOMAINS[0];",
    logic
)

content = content.replace("DOMAINS.map((domain)", "domains.map((domain)")
content = content.replace("domain.id", "domain.domain_id")

content = content.replace(
    """<button
                key={domain.domain_id}
                onClick={() => {
                  onSelectDomain(domain.domain_id);
                  setDropdownOpen(false);
                }}
                className={clsx(
                  'w-full text-left px-3 py-2 rounded-lg text-xs font-mono transition-colors flex flex-col',
                  domain.domain_id === selectedDomain
                    ? 'bg-cyan-500/10 text-cyan-300 font-semibold border border-cyan-500/30'
                    : 'text-slate-300 hover:bg-slate-800'
                )}
              >
                <span>{domain.name}</span>
                <span className="text-[10px] text-slate-500 font-normal">{domain.subtitle}</span>
              </button>""",
    """<button
                key={domain.domain_id}
                onClick={() => {
                  if (domain.status === 'verified') {
                    onSelectDomain(domain.domain_id);
                    setDropdownOpen(false);
                  }
                }}
                disabled={domain.status !== 'verified'}
                title={domain.status === 'planned' ? 'Not yet backed by a verified result' : domain.status === 'partial' ? 'Partially verified — see Protocol & Limits' : ''}
                className={clsx(
                  'w-full text-left px-3 py-2 rounded-lg text-xs font-mono transition-colors flex flex-col',
                  domain.domain_id === selectedDomain
                    ? 'bg-cyan-500/10 text-cyan-300 font-semibold border border-cyan-500/30'
                    : domain.status !== 'verified' 
                    ? 'text-slate-500 opacity-50 cursor-not-allowed'
                    : 'text-slate-300 hover:bg-slate-800'
                )}
              >
                <span>{domain.name} {domain.status !== 'verified' && `(${domain.status})`}</span>
              </button>"""
)

with open("web/src/components/TopBar.tsx", "w") as f:
    f.write(content)
