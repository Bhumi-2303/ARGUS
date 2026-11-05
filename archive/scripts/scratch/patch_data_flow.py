import re

with open("web/src/features/analysis/InputAnalysisPage.tsx", "r") as f:
    code = f.read()

code = code.replace("setSelectedSample(sample);", "setSelectedSample(sample);\n    localStorage.setItem('argus_active_sample', JSON.stringify(sample));")

with open("web/src/features/analysis/InputAnalysisPage.tsx", "w") as f:
    f.write(code)

with open("web/src/features/explain/ExplainabilityPage.tsx", "r") as f:
    code2 = f.read()

old_query = """  const { data: samples } = useQuery({
    queryKey: ['samples_explain'],
    queryFn: async () => {
      const res = await fetch('http://localhost:8000/api/v1/data/samples');
      const data = await res.json();
      if (data && data.length > 0 && !features) {
        setFeatures(data[0].features);
      }
      return data;
    }
  });"""

new_query = """  const { data: samples } = useQuery({
    queryKey: ['samples_explain'],
    queryFn: async () => {
      const res = await fetch('http://localhost:8000/api/v1/data/samples');
      const data = await res.json();
      if (data && data.length > 0 && !features) {
        const stored = localStorage.getItem('argus_active_sample');
        if (stored) {
            try {
                const parsed = JSON.parse(stored);
                if (parsed && parsed.features) {
                    setFeatures(parsed.features);
                    return data;
                }
            } catch (e) {}
        }
        setFeatures(data[0].features);
      }
      return data;
    }
  });"""
code2 = code2.replace(old_query, new_query)

with open("web/src/features/explain/ExplainabilityPage.tsx", "w") as f:
    f.write(code2)
