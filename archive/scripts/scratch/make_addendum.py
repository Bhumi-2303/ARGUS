report = []
report.append("# DG DATA AUDIT - ADDENDUM")

# 1. NF-ToN-IoT
report.append("\n## 1. NF-ToN-IoT Deep Dive")
report.append("- **Filename**: `data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet`")
report.append("- **Format**: Parquet")
report.append("- **Compression**: Snappy [REQUIRES VERIFICATION of internal block compression]")
report.append("- **Size on Disk**: 9.05 MB (9,491,944 bytes)")
report.append("- **Columns (12)**: `L4_SRC_PORT`, `L4_DST_PORT`, `PROTOCOL`, `L7_PROTO`, `IN_BYTES`, `OUT_BYTES`, `IN_PKTS`, `OUT_PKTS`, `TCP_FLAGS`, `FLOW_DURATION_MILLISECONDS`, `Label`, `Attack`")
report.append("- **Label Columns**: `Label` (integer), `Attack` (string category)")
report.append("- **Row Count (Independent Method)**: `1,157,994` (Read directly via standard DataFrame loader and length methods)")
report.append("- **Class Counts**: 198,450 Benign, 959,544 Attack")

report.append("\n### Investigation of Earlier Tracking Numbers")
report.append("A repository-wide search for `NF-ToN-IoT-v2`, `13135881`, `10508704`, and `1313588` reveals that earlier phase3/phase4 experiments absolutely utilized a much larger dataset. Specifically:")
report.append("1. **`training/scripts/phase3_execute_all.py`** explicitly refers to `NF-ToN-IoT-v2 (10,508,704 train / 2,627,177 test)` (Totaling exactly `13,135,881`).")
report.append("2. This data was loaded from `ARGUS_Cross_Domain_Results/argus_coral_data/nfton_train_features.csv`.")
report.append("3. **Conclusion**: That directory and CSV file are entirely **missing** from this machine. The previous researchers performed their alignment (CORAL/DANN) on the full 13.1M-row NF-ToN-IoT-v2 generated feature set, which is physically absent from the current workspace. Therefore, this is not a tracking error; the data was simply left behind or deleted prior to this audit.")

# 2. TON_IoT
report.append("\n## 2. TON_IoT File State")
report.append("- **File End Check**: The file `train_test_network.csv` ends with a complete, well-formed row (`...0,0,0,-,-,-,-,-,-,1,xss`), meaning the file is not a randomly severed byte-stream.")
report.append("- **Row Count Comparison**: The file has exactly 211,043 data rows (211,044 lines). The earlier manifest reported 461,043 rows. ")
report.append("- **ZIP Member Check**: No source ZIP archives (e.g., `ton_iot.zip`) exist anywhere on the machine to compare member sizes against. [REQUIRES VERIFICATION of original ZIP availability].")
report.append("- **Conclusion**: Because the file ends cleanly on a newline boundary but is missing exactly ~250,000 rows compared to the canonical 461k Train/Test set, this file is a truncated or sub-sampled copy (likely generated via `head -n 211044` or pandas `.head()`).")
report.append("- **Label Counts**: 50,000 Benign (0), 161,043 Attack (1)")

# 5. Feasibility Table
report.append("\n## 5. Feature Translation Feasibility Table")
report.append("| Feature | NF-ToN-IoT | TON_IoT | BoT-IoT | CICIoT2023 |")
report.append("|---|---|---|---|---|")
report.append("| `duration` | `FLOW_DURATION_MILLISECONDS` | `duration` | `dur` | [MISSING] (Only derived IAT available) |")
report.append("| `src_pkts` | `IN_PKTS` | `src_pkts` | `spkts` | [MISSING] |")
report.append("| `dst_pkts` | `OUT_PKTS` | `dst_pkts` | `dpkts` | [MISSING] |")
report.append("| `src_bytes` | `IN_BYTES` | `src_bytes` | `sbytes` | [MISSING] (Only 'Tot sum') |")
report.append("| `dst_bytes` | `OUT_BYTES` | `dst_bytes` | `dbytes` | [MISSING] |")
report.append("| `protocol` | `PROTOCOL` | `proto` | `proto` | `Protocol Type` |")
report.append("| `pkt_mean_to_max` (ARGUS) | NO (No Max Pkt) | NO (No Max Pkt) | YES (`mean`, `max`) | YES (`AVG`, `Max`) |")
report.append("| `tcp_flag_density` (ARGUS) | YES (`TCP_FLAGS`) | NO (No Flags) | YES (`flgs`) | YES (Extensive Flags) |")
report.append("| `log_pkt_mean` (ARGUS) | YES (Derived from Bytes/Pkts) | YES (Derived) | YES (`mean`) | YES (`AVG`) |")
report.append("| `log_pkt_max` (ARGUS) | NO | NO | YES (`max`) | YES (`Max`) |")
report.append("\n*Note: Calculating the four custom ARGUS features is fundamentally impossible across all four datasets simultaneously due to disjoint base schemas.*")

with open("scratch/addendum_base.py", "w") as f:
    f.write(repr(report))

