# Domain Leakage Audit

To prevent models from memorizing the dataset environment rather than the attack pattern, the following leakage features MUST be explicitly managed.

## Identified Leakage Features

### 1. IP Addresses (Source / Destination)
*   **Present in**: `NF-ToN-IoT` (IPV4_SRC_ADDR, IPV4_DST_ADDR), `BoT-IoT` (saddr, daddr), `TON_IoT` (src_ip, dst_ip).
*   **Verdict**: **EXCLUDE FROM DG EXPERIMENTS**. IPs are perfectly correlated with the lab environment (e.g., BoT-IoT uses `192.168.100.x`). A model will memorize these subnets and fail to generalize.

### 2. MAC Addresses
*   **Present in**: `BoT-IoT` (smac, dmac).
*   **Verdict**: **EXCLUDE FROM DG EXPERIMENTS**. Device-specific hardware identifiers instantly overfit to the testbed hardware.

### 3. Ports
*   **Present in**: `NF-ToN-IoT` (L4_SRC_PORT, L4_DST_PORT), `BoT-IoT` (sport, dport), `TON_IoT` (src_port, dst_port).
*   **Verdict**: **TRANSFORM**. Destination ports (e.g., 80, 443) are useful for identifying services, but high-ephemeral source ports introduce noise. Recommend grouping destination ports into categorical bins (Web, DNS, SSH, etc.) and dropping raw port numbers.

### 4. Row / Flow Identifiers
*   **Present in**: `BoT-IoT` (pkSeqID, seq).
*   **Verdict**: **EXCLUDE**. Sequential IDs leak the temporal sorting of attacks in the dataset and provide no behavioral signal.

### 5. Physical OT Interlocks (HAI)
*   **Present in**: `HAI` (P2_TripEx - Trip signal).
*   **Verdict**: **RETAIN BUT MONITOR**. Some physical variables act as perfect deterministic triggers for an attack label. If the goal is early detection, variables representing the *system's own alert mechanism* must be dropped to prevent target leakage.
