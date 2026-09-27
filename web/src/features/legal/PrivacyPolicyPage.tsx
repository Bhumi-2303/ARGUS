import React from 'react';
import { Card } from '../../components/Card';

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-900 dark:text-white mb-2">
          Privacy Policy
        </h1>
        <p className="text-slate-500">Effective Date: {new Date().toLocaleDateString()}</p>
      </div>

      <Card className="p-8 space-y-6 text-sm text-slate-700 dark:text-slate-300">
        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">1. Data Collection and Usage</h2>
          <p>
            ARGUS is a research platform designed for network traffic classification and explainability. 
            When utilizing the platform, you may select or upload dataset samples (e.g., PCAP, Parquet, or JSON formats) for inference.
          </p>
          <p>
            The system temporarily processes these features in memory to execute the multi-agent prediction pipeline. 
            Data provided during active analysis is not persisted beyond the lifecycle of the session unless explicitly saved as part of a verified experimental trace.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">2. Logging and Telemetry</h2>
          <p>
            For debugging and scientific validation, ARGUS captures execution traces of the multi-agent graph, including prediction probabilities and model versions. These logs are stored locally on the deployment server and are not transmitted to third-party analytics services.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">3. Third-Party Integrations</h2>
          <p>
            The ARGUS Knowledge Context Agent may query external knowledge bases (e.g., MITRE ATT&CK framework). No user-submitted network traffic or personally identifiable information is transmitted during these queries.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">4. Local Storage</h2>
          <p>
            The ARGUS frontend utilizes local browser storage strictly for maintaining transient state across UI views (e.g., preserving the active sample between the Input and Explanation views).
          </p>
        </section>
      </Card>
    </div>
  );
}
