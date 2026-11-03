with open("web/src/features/monitor/LiveMonitorPage.tsx", "r") as f:
    content = f.read()

# Add useQuery and DomainInfo / ModelInfo if not present
if "useQuery" not in content:
    content = content.replace("import { useState, useEffect, useRef } from 'react';", "import { useState, useEffect, useRef } from 'react';\nimport { useQuery } from '@tanstack/react-query';")

content = content.replace(
    """  // Available domain options
  const domainOptions = [
    { id: 'nfton', name: 'NF-ToN-IoT-v2 (Target Smart Home)' },
    { id: 'iec104', name: 'IEC 60870-5-104 (Target SCADA Substation)' },
    { id: 'ciciot', name: 'CICIoT2023 (Source Enterprise)' },
  ];

  // Available model options
  const modelOptions = [
    { id: 'model_d2_coral', name: 'Clean Class-Aware CORAL (D2)' },
    { id: 'xgb_source', name: 'XGBoost Source-Only (Unadapted)' },
    { id: 'model_d1_baseline', name: 'LightGBM D1 Baseline' },
    { id: 'model_d3_native', name: 'D3 Native SCADA Model' },
  ];""",
    """  // Dynamic fetching of available domains and models
  const { data: domainsData } = useQuery({ queryKey: ['domains'], queryFn: api.getDomains });
  const { data: modelsData } = useQuery({ queryKey: ['models'], queryFn: api.getModels });
  const domainOptions = domainsData?.domains || [];
  const modelOptions = modelsData?.models || [];
"""
)

# Update JSX domain mapping
content = content.replace(
    """            <select
              id="domain-select"
              value={selectedDomain}
              onChange={(e) => handleDomainChange(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
            >
              {domainOptions.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>""",
    """            <select
              id="domain-select"
              value={selectedDomain}
              onChange={(e) => handleDomainChange(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
            >
              {domainOptions.map((d) => (
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

# Update JSX model checkboxes
content = content.replace(
    """            {modelOptions.map((m) => (
              <label
                key={m.id}
                className="inline-flex items-center gap-1.5 text-xs font-mono text-slate-300 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedModels.includes(m.id)}
                  onChange={() => toggleModelSelection(m.id)}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-slate-900"
                />
                <span>{m.name}</span>
              </label>
            ))}""",
    """            {modelOptions.map((m) => {
              const disabled = m.status !== 'verified';
              return (
              <label
                key={m.model_id}
                title={disabled ? (m.status === 'planned' ? 'Not yet backed by a verified result' : 'Partially verified — see Protocol & Limits') : ''}
                className={`inline-flex items-center gap-1.5 text-xs font-mono cursor-pointer ${disabled ? 'text-slate-500 opacity-50' : 'text-slate-300'}`}
              >
                <input
                  type="checkbox"
                  checked={selectedModels.includes(m.model_id)}
                  onChange={() => toggleModelSelection(m.model_id)}
                  disabled={disabled}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-slate-900 disabled:opacity-50"
                />
                <span>{m.name} {disabled ? `(${m.status})` : ''}</span>
              </label>
            )})}"""
)

with open("web/src/features/monitor/LiveMonitorPage.tsx", "w") as f:
    f.write(content)
