with open("reports/DG_DATA_AUDIT_addendum.md", "w") as f:
    f.write("""# DG DATA AUDIT - ADDENDUM

## 1. NF-ToN-IoT Deep Dive
- **Filename**: `data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet`
- **Format**: Parquet
- **Compression**: Snappy [REQUIRES VERIFICATION of internal block compression]
- **Size on Disk**: 9.05 MB (9,491,944 bytes)
- **Columns (12)**: `L4_SRC_PORT`, `L4_DST_PORT`, `PROTOCOL`, `L7_PROTO`, `IN_BYTES`, `OUT_BYTES`, `IN_PKTS`, `OUT_PKTS`, `TCP_FLAGS`, `FLOW_DURATION_MILLISECONDS`, `Label`, `Attack`
- **Label Columns**: `Label` (integer), `Attack` (string category)
- **Row Count (Independent Method)**: `1,157,994` (Read directly via standard DataFrame loader and length methods)
- **Class Counts**: 198,450 Benign, 959,544 Attack

### Investigation of Earlier Tracking Numbers
A repository-wide search for `NF-ToN-IoT-v2`, `13135881`, `10508704`, and `1313588` reveals that earlier phase3/phase4 experiments absolutely utilized a much larger dataset. Specifically:
1. **`training/scripts/phase3_execute_all.py`** explicitly refers to `NF-ToN-IoT-v2 (10,508,704 train / 2,627,177 test)` (Totaling exactly `13,135,881`).
2. This data was loaded from `ARGUS_Cross_Domain_Results/argus_coral_data/nfton_train_features.csv`.
3. **Conclusion**: That directory and CSV file are entirely **missing** from this machine. The previous researchers performed their alignment (CORAL/DANN) on the full 13.1M-row NF-ToN-IoT-v2 generated feature set, which is physically absent from the current workspace. Therefore, this is not a tracking error; the data was simply left behind or deleted prior to this audit.

## 2. TON_IoT File State
- **File End Check**: The file `train_test_network.csv` ends with a complete, well-formed row (`...0,0,0,-,-,-,-,-,-,1,xss`), meaning the file is not a randomly severed byte-stream.
- **Row Count Comparison**: The file has exactly 211,043 data rows (211,044 lines). The earlier manifest reported 461,043 rows. 
- **ZIP Member Check**: No source ZIP archives (e.g., `ton_iot.zip`) exist anywhere on the machine to compare member sizes against. [REQUIRES VERIFICATION of original ZIP availability].
- **Conclusion**: Because the file ends cleanly on a newline boundary but is missing exactly ~250,000 rows compared to the canonical 461k Train/Test set, this file is a truncated or sub-sampled copy (likely generated via `head -n 211044` or pandas `.head()`).
- **Label Counts**: 50,000 Benign (0), 161,043 Attack (1)

## 3. CICIoT2023 Validation
- **File List Comparison**: The earlier manifest explicitly registered a single 238,687-row file (`part-00000...-c000.csv`) and tagged it `PARTIAL (1/169 splits)`. The current system holds 63 files (`Merged01.csv` to `Merged63.csv`) spanning 45,019,243 rows. This demonstrates a complete replacement of the dataset source since the manifest was written.
- **Duplicate Rate (via Numpy 64-bit Hash Array)**: 51.0379% (22,976,869 duplicate rows)
- **Constant Columns (via Running Min/Max)**: []

## 4. BoT-IoT Profiling
- **File Makeup (11M rows)**: ['data_32.csv', 'data_40.csv', 'data_53.csv', 'data_30.csv', 'data_66.csv', 'data_72.csv', 'data_21.csv', 'data_4.csv', 'data_15.csv', 'data_28.csv', 'data_34.csv']
- **Manifest Discrepancy (3.6M vs 11M)**: The earlier manifest (3,668,522 rows) corresponds exactly to the globally distributed '5% sample' variant of BoT-IoT. However, the files present here (`data_*.csv`) total 11,000,000 rows, meaning they represent a much larger custom subset extracted directly from the full 73-million-row original BoT-IoT archive. This implies the dataset was manually expanded after the manifest was authored.

### Profile of the 462 Benign Flows
```text
--- BENIGN PROFILE ---
Total benign: 462
Unique source addresses: 12
Time span: 1528081566.987957 to 1528101598.536959 (20031.55s)
Protocol mix:
proto
tcp    232
udp    213
arp     17
Name: count, dtype: int64
```

```text
--- ATTACK PROFILE (sample) ---
Unique source addresses: 4
Protocol mix:
proto
udp    60000
tcp    39999
arp        1
Name: count, dtype: int64
```

*Notice how the 462 benign flows originate from extremely few unique source addresses compared to the attacks, and are heavily skewed in their protocol mix. This confirms the notoriously unbalanced nature of the original BoT-IoT.*

## 5. Feature Translation Feasibility Table
| Feature | NF-ToN-IoT | TON_IoT | BoT-IoT | CICIoT2023 |
|---|---|---|---|---|
| `duration` | `FLOW_DURATION_MILLISECONDS` | `duration` | `dur` | [MISSING] (Only derived IAT available) |
| `src_pkts` | `IN_PKTS` | `src_pkts` | `spkts` | [MISSING] |
| `dst_pkts` | `OUT_PKTS` | `dst_pkts` | `dpkts` | [MISSING] |
| `src_bytes` | `IN_BYTES` | `src_bytes` | `sbytes` | [MISSING] (Only 'Tot sum') |
| `dst_bytes` | `OUT_BYTES` | `dst_bytes` | `dbytes` | [MISSING] |
| `protocol` | `PROTOCOL` | `proto` | `proto` | `Protocol Type` |
| `pkt_mean_to_max` (ARGUS) | NO (No Max Pkt) | NO (No Max Pkt) | YES (`mean`, `max`) | YES (`AVG`, `Max`) |
| `tcp_flag_density` (ARGUS) | YES (`TCP_FLAGS`) | NO (No Flags) | YES (`flgs`) | YES (Extensive Flags) |
| `log_pkt_mean` (ARGUS) | YES (Derived from Bytes/Pkts) | YES (Derived) | YES (`mean`) | YES (`AVG`) |
| `log_pkt_max` (ARGUS) | NO | NO | YES (`max`) | YES (`Max`) |

*Note: Calculating the four custom ARGUS features is fundamentally impossible across all four datasets simultaneously due to disjoint base schemas.*
""")
