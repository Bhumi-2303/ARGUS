import json

with open("audit_metrics.json") as f:
    metrics = json.load(f)

report = ["# DG DATA AUDIT - ADDENDUM 2\n"]
report.append("## A. Feasibility Matrix")
report.append("Matrix constructed purely from column headers (no row scanning).")
report.append("")
report.append("| Dataset | duration | src_pkts | dst_pkts | src_bytes | dst_bytes | total_pkts | total_bytes | protocol | tcp_flags | max_pkt_len | pkt_mean_to_max | tcp_flag_density | log_pkt_mean | log_pkt_max |")
report.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

# Logic for mapping
# NF-ToN-IoT
report.append("| **CICIoT2023** | absent (only IAT available) | absent | absent | absent | absent | present (`Number`) | present (`Tot size`) | present (`Protocol Type`) | derivable (via specific flag columns) | present (`Max`) | derivable (`AVG`/`Max`) | derivable (flag cols) | derivable (`AVG`) | derivable (`Max`) |")
report.append("| **NF-ToN-IoT** | present (`FLOW_DURATION_MILLISECONDS`) | present (`IN_PKTS`) | present (`OUT_PKTS`) | present (`IN_BYTES`) | present (`OUT_BYTES`) | derivable (`IN_PKTS`+`OUT_PKTS`) | derivable (`IN_BYTES`+`OUT_BYTES`) | present (`PROTOCOL`) | present (`TCP_FLAGS`) | absent | absent | derivable (`TCP_FLAGS`/pkts) | derivable | absent |")
report.append("| **TON_IoT** | present (`duration`) | present (`src_pkts`) | present (`dst_pkts`) | present (`src_bytes`) | present (`dst_bytes`) | derivable (`src_pkts`+`dst_pkts`) | derivable (`src_bytes`+`dst_bytes`) | present (`proto`) | absent | absent | absent | absent | derivable | absent |")
report.append("| **BoT-IoT** | present (`dur`) | present (`spkts`) | present (`dpkts`) | present (`sbytes`) | present (`dbytes`) | derivable (`pkts`) | derivable (`bytes`) | present (`proto`) | present (`flgs`) | present (`max`) | derivable (`mean`/`max`) | derivable (`flgs`/pkts) | derivable (`mean`) | derivable (`max`) |")
report.append("")

with open("reports/DG_DATA_AUDIT_addendum2.md", "w") as f:
    f.write("\n".join(report))
print("Step A complete")
