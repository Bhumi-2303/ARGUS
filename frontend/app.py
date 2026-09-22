import streamlit as st
import pandas as pd
import json
import requests
import matplotlib.pyplot as plt
import os

API_URL = "http://localhost:8000/analyze"

st.set_page_config(page_title="ARGUS Dashboard", layout="wide")

st.title("ARGUS — Autonomous Risk-aware Grid Understanding & Security")

# Claim Boundary Panel
st.sidebar.header("Claim Boundary")
st.sidebar.markdown("""
- **No calibrated risk score**
- **1 Source & 1 Target Dataset**
- **Batch replay only** (no real-time streaming)
- **Seed Count:** 42 (As reported in results)
""")

# Results Summary
st.sidebar.header("Day 4 Results")
results_path = "artifacts/day4/results.json"
if os.path.exists(results_path):
    with open(results_path, "r") as f:
        res = json.load(f)
    st.sidebar.write(f"**Selected Candidate:** {res['winner']}")
    st.sidebar.write("**Mixed Stream (Candidate C):**")
    st.sidebar.text(json.dumps(res['mixed']['C'], indent=2))
else:
    st.sidebar.write("Results not found.")

# Main Interaction
st.header("Batch Replay / Upload")
uploaded_file = st.file_uploader("Upload CSV/Parquet Flow Data", type=["csv", "parquet"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_parquet(uploaded_file)
    
    st.write(f"Loaded {len(df)} flows.")
    
    if st.button("Run Pipeline"):
        with st.spinner("Analyzing via Orchestrator..."):
            features = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']
            # Take a small batch to not overload the API for the demo
            batch = df[features].head(50).to_dict(orient="records")
            
            try:
                response = requests.post(API_URL, json={"flows": batch})
                result = response.json()
                
                # Agent Status Panel
                st.subheader("Agent Status Panel")
                not_implemented = result.get("not_implemented_agents", [])
                st.write("**Not Implemented:**", ", ".join(not_implemented) if not_implemented else "None")
                
                # We expect explainability results to be under results -> Explainability
                exp_res = result.get("results", {}).get("Explainability", {})
                if exp_res:
                    st.subheader("Drift & Explainability")
                    st.write(f"**Explanation Stability (Spearman):** {exp_res.get('explanation_stability', 'N/A')}")
                    
                    st.write("### Predictions & Global SHAP")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("Source Model Global SHAP")
                        source_shap = exp_res.get("global_mean_attribution_source", {})
                        if source_shap:
                            fig, ax = plt.subplots()
                            ax.bar(source_shap.keys(), source_shap.values())
                            plt.xticks(rotation=45)
                            st.pyplot(fig)
                            
                    with col2:
                        st.write("Adapted Model Global SHAP")
                        adapted_shap = exp_res.get("global_mean_attribution_adapted", {})
                        if adapted_shap:
                            fig, ax = plt.subplots()
                            ax.bar(adapted_shap.keys(), adapted_shap.values())
                            plt.xticks(rotation=45)
                            st.pyplot(fig)
                            
            except Exception as e:
                st.error(f"Error communicating with API: {e}")
