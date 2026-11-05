# Feature Space & Schema Audit

This document assesses raw field availability and definitions across evaluated domains to ensure any new feature spaces are provably universal, not dataset-specific.

## 1. Raw Schemas & Data Types

### CICIoT2023 (`Merged01.csv`)
*   **Header_Length** (float64): Unconfirmed meaning (sum of headers?)
*   **Protocol Type** (int64): Protocol number
*   **Time_To_Live** (float64): TTL value
*   **Rate** (float64): Unconfirmed (packets/sec or bytes/sec?)
*   **fin_flag_number, syn_flag_number, etc.** (float64): TCP flag occurrence counts
*   **ack_count, syn_count, etc.** (int64): TCP flag counts
*   **HTTP, HTTPS, DNS, etc.** (float64): L7/L4 protocol boolean flags
*   **Tot sum** (int64): Unconfirmed meaning (likely Total Bytes based on external documentation)
*   **Min, Max, AVG, Std** (int64/float64): Unconfirmed meaning (packet size or IAT stats?)
*   **Tot size** (float64): Unconfirmed meaning (Total Bytes?)
*   **IAT** (float64): Inter-Arrival Time
*   **Number** (int64): Unconfirmed meaning (likely Total Packets)
*   **Variance** (float64): Unconfirmed meaning
*   **Label** (str): Attack/Benign label

### NF-ToN-IoT-v2 (`NF-ToN-IoT.parquet`)
*   **L4_SRC_PORT, L4_DST_PORT** (int32): Source/Destination Ports
*   **PROTOCOL** (int8): Protocol number
*   **L7_PROTO** (float32): Layer 7 Protocol
*   **IN_BYTES, OUT_BYTES** (int32): Forward/Backward Byte counts
*   **IN_PKTS, OUT_PKTS** (int32): Forward/Backward Packet counts
*   **TCP_FLAGS** (int16): TCP flags bitmask
*   **FLOW_DURATION_MILLISECONDS** (int32): Flow duration in milliseconds
*   **Label, Attack** (int8, str): Labels

### BoT-IoT (`data_32.csv`)
*   **pkSeqID** (int64): Row identifier
*   **stime, ltime** (float64): Start/last timestamps
*   **flgs** (str): TCP flags state string (Argus format)
*   **proto** (str): Protocol name ('tcp', 'udp')
*   **saddr, daddr, sport, dport** (str/int): IP/Ports
*   **pkts, bytes** (int64): Total packets / Total bytes
*   **state** (str): Transaction state
*   **seq** (int64): Sequence number
*   **dur** (float64): Flow duration in seconds
*   **mean, stddev, sum, min, max** (float64): Unconfirmed (likely duration or packet size stats)
*   **smac, dmac, soui, doui, sco, dco** (float64): MAC/OUI info
*   **spkts, dpkts** (int64): Forward/Backward packets
*   **sbytes, dbytes** (int64): Forward/Backward bytes
*   **rate, srate, drate** (float64): Packets per second rates
*   **attack, category, subcategory** (int64/str): Labels

### TON_IoT (`Network_dataset_1.csv`)
*   **ts** (str): Timestamp
*   **src_ip, dst_ip, src_port, dst_port** (str/int): IPs and Ports
*   **proto** (str): Protocol name
*   **service** (str): L7 Service
*   **duration** (float64): Flow duration
*   **src_bytes, dst_bytes** (int64): Forward/Backward payload bytes
*   **src_pkts, dst_pkts** (int64): Forward/Backward packets
*   **src_ip_bytes, dst_ip_bytes** (int64): Forward/Backward total bytes
*   **conn_state** (str): Connection state
*   **dns_*, ssl_*, http_*** (mixed): L7 fields
*   **weird_*** (str): Zeek notices
*   **label, type** (int64/str): Labels

### HAI (`hai-test1.csv`)
*   **timestamp** (str): Time of observation
*   **P1_FCV01D, P1_PIT01, etc.** (float64/int64): Physical ICS process data (sensors/actuators).
*   *Note: Not flow records. No network schema compatibility.*

---

## 2. Universal Canonical Mapping Table

| Canonical Concept | CICIoT2023 | NF-ToN-IoT-v2 | BoT-IoT | TON_IoT | Cross-Domain Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Packets** | `Number` (Unconfirmed) | Derivable (`IN_PKTS + OUT_PKTS`) | `pkts` | Derivable (`src_pkts + dst_pkts`) | ✅ **Safely Common** |
| **Total Bytes** | `Tot sum` or `Tot size` (Unconfirmed) | Derivable (`IN_BYTES + OUT_BYTES`) | `bytes` | Derivable (`src_ip_bytes + dst_ip_bytes`) | ✅ **Safely Common** |
| **Protocol** | `Protocol Type` | `PROTOCOL` | `proto` | `proto` | ✅ **Safely Common** |
| **Flow Duration** | Absent (Or indirectly derivable) | `FLOW_DURATION_MILLISECONDS` | `dur` | `duration` | ⚠️ **Derivable-but-not-direct** (Missing in CICIoT2023 directly) |
| **Rates (Pkt/Byte)** | `Rate` | Derivable (`pkts / duration`) | `rate`, `srate`, `drate` | Derivable (`pkts / duration`) | ⚠️ **Derivable-but-not-direct** (Missing in NF-ToN & TON directly) |
| **Fwd/Bwd Pkt Split** | Absent | `IN_PKTS`, `OUT_PKTS` | `spkts`, `dpkts` | `src_pkts`, `dst_pkts` | ❌ **Dataset-Specific** (Missing in CICIoT2023) |
| **Fwd/Bwd Byte Split**| Absent | `IN_BYTES`, `OUT_BYTES` | `sbytes`, `dbytes` | `src_bytes`, `dst_bytes` | ❌ **Dataset-Specific** (Missing in CICIoT2023) |
| **Inter-Arrival Time**| `IAT` | Absent | Absent (Unconfirmed if `mean` is IAT) | Absent | ❌ **Dataset-Specific** (Only confirmed in CICIoT2023) |
| **Timestamps** | Absent | Absent | `stime`, `ltime` | `ts` | ❌ **Dataset-Specific** (Missing in CICIoT2023 & NF-ToN) |
