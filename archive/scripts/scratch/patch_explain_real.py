import re

with open("web/src/features/explain/ExplainabilityPage.tsx", "r") as f:
    code = f.read()

# Replace hardcoded features with fetched sample
code = code.replace("""  const [features, setFeatures] = useState({
    pkt_mean_to_max: 0.35,
    tcp_flag_density: 0.72,
    log_pkt_mean: 4.85,
    log_pkt_max: 6.12,
  });""", """  const [features, setFeatures] = useState<any>(null);

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
  });""")

with open("web/src/features/explain/ExplainabilityPage.tsx", "w") as f:
    f.write(code)
