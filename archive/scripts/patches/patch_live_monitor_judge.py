import re
with open("web/src/features/monitor/LiveMonitorPage.tsx", "r") as f:
    content = f.read()

# Add prop
content = re.sub(
    r"export default function LiveMonitorPage\(\) \{",
    r"export default function LiveMonitorPage({ isJudgeMode = false }: { isJudgeMode?: boolean }) {",
    content
)

# Judge mode logic
judge_logic = """
  // Judge Mode Orchestration
  const [judgeStep, setJudgeStep] = useState(0);
  const [judgeCaption, setJudgeCaption] = useState("");
  
  useEffect(() => {
    if (!isJudgeMode) return;
    
    // Step 1: In-Domain Performance (0s)
    setJudgeStep(1);
    setSelectedDomain('ciciot');
    setSelectedModels(['model_d1_baseline', 'xgb_source']);
    setJudgeCaption("STAGE 1: In-Domain Evaluation. Enterprise models running natively on CICIoT with high accuracy.");
    setIsStreaming(true);
    
    // Step 2: Domain Switch (8s)
    const t1 = setTimeout(() => {
      setJudgeStep(2);
      setSelectedDomain('nfton');
      setJudgeCaption("STAGE 2: Domain Switch! Traffic suddenly shifts to NF-ToN-IoT-v2. Watch the baseline models completely collapse and generate false positives.");
    }, 8000);
    
    // Step 3: Shift Alert (16s)
    const t2 = setTimeout(() => {
      setJudgeStep(3);
      setJudgeCaption("STAGE 3: Shift Alert! The Data Intelligence agent detects severe statistical drift (PSI > 0.2) in packet size distributions.");
    }, 16000);
    
    // Step 4: Adaptation (22s)
    const t3 = setTimeout(() => {
      setJudgeStep(4);
      setJudgeCaption("STAGE 4: Adaptation. Unsupervised Class-Aware CORAL is dynamically recalculating target domain covariance matrices...");
      setIsStreaming(false);
    }, 22000);
    
    // Step 5: Recovery (26s)
    const t4 = setTimeout(() => {
      setJudgeStep(5);
      setSelectedModels(['model_d1_baseline', 'model_d2_coral']);
      setJudgeCaption("STAGE 5: Recovery! The new Leakage-Controlled CORAL model deploys and restores discriminative capability.");
      setIsStreaming(true);
    }, 26000);
    
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); clearTimeout(t4); };
  }, [isJudgeMode]);
"""

# Insert just inside component
content = content.replace("export default function LiveMonitorPage({ isJudgeMode = false }: { isJudgeMode?: boolean }) {", "export default function LiveMonitorPage({ isJudgeMode = false }: { isJudgeMode?: boolean }) {\n" + judge_logic)

# Add Judge mode banner
banner_html = """
      {isJudgeMode && (
        <div className="bg-indigo-950/80 border-2 border-indigo-500 p-4 rounded-xl shadow-2xl flex items-center justify-between mb-4 animate-in fade-in slide-in-from-top-4">
          <div className="space-y-1">
            <h2 className="text-indigo-400 font-black tracking-widest uppercase text-xs">AUTO-PILOT: JUDGE MODE</h2>
            <p className="text-slate-100 font-mono text-sm">{judgeCaption}</p>
          </div>
          <button onClick={() => setIsStreaming(!isStreaming)} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded text-white font-bold text-xs uppercase transition-colors">
            {isStreaming ? 'Pause Scenario' : 'Resume Scenario'}
          </button>
        </div>
      )}
"""

content = content.replace('<div className="space-y-6 pb-12 max-w-[1600px] mx-auto">', '<div className="space-y-6 pb-12 max-w-[1600px] mx-auto">\n' + banner_html)

with open("web/src/features/monitor/LiveMonitorPage.tsx", "w") as f:
    f.write(content)
