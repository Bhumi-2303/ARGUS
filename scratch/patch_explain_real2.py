import re

with open("web/src/features/explain/ExplainabilityPage.tsx", "r") as f:
    code = f.read()

old_query = """  const [features, setFeatures] = useState<any>(null);

  // Fetch real samples for explanation input
  const { data: samples } = useQuery({
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

new_query = """  // Fetch real samples for explanation input
  const { data: samples } = useQuery({
    queryKey: ['samples_explain'],
    queryFn: async () => {
      const res = await fetch('http://localhost:8000/api/v1/data/samples');
      return await res.json();
    }
  });
  const features = samples && samples.length > 0 ? samples[0].features : null;
"""
code = code.replace(old_query, new_query)

# Change handleExplain to guard on features
code = code.replace("""  const handleExplain = () => {
    explainMutation.mutate({
      model_name: selectedModel,
      features,
    });
  };""", """  const handleExplain = () => {
    if (!features) return;
    explainMutation.mutate({
      model_name: selectedModel,
      features,
    });
  };""")

with open("web/src/features/explain/ExplainabilityPage.tsx", "w") as f:
    f.write(code)
