# Methodology Module 02: Feature Harmonization & Resolution Scaling

**Document Status**: Official Research Methodology Specification  
**Associated Manuscript**: Section III (Methodology) & Section V-D (Representation Scaling)

---

## 1. The Cross-Domain Representation Problem

Network intrusion detection datasets exhibit extreme schema heterogeneity:
- **D1 (CICIoT2023)** records 46 statistical features derived from raw packet timings, inter-arrival intervals, and header flags.
- **D2 (NF-ToN-IoT-v2)** records 43 Cisco NetFlow-v9 standardized features aggregated at flow termination.
- **D3 (IEC 60870-5-104)** records 70 industrial telemetry variables including ASDU type IDs, COT (cause of transmission), information object addresses (IOA), and physical grid analog measurements.

Supervised transfer learning directly between these raw feature spaces is impossible because models trained on D1 cannot ingest D2 or D3 schemas. To enable cross-domain inference, a **synthesized common feature representation** must be constructed from invariant network transport properties.

---

## 2. Core Common Representation: ARGUS-4

The primary harmonized representation, **ARGUS-4**, defines four behavioral features computable across any bidirectional IP flow regardless of underlying collector architecture:

$$\Phi_{\text{ARGUS-4}}(x) = \begin{bmatrix} f_{\text{pkt\_ratio}} \\ f_{\text{tcp\_flags}} \\ f_{\text{log\_mean}} \\ f_{\text{log\_max}} \end{bmatrix}$$

### Mathematical Definitions

1. **Packet Symmetry Ratio ($f_{\text{pkt\_ratio}}$)**:
   Measures transmission symmetry and flow directionality:
   $$f_{\text{pkt\_ratio}} = \frac{\mu_{\text{pkt}}}{\max_{\text{pkt}} + \epsilon} \in (0, 1]$$
   - Captures asymmetric flooding attacks (e.g., SYN floods, UDP amplification) where packet lengths are uniform, forcing the ratio to $\approx 1.0$.

2. **TCP Control Flag Density ($f_{\text{tcp\_flags}}$)**:
   Quantifies anomalous transport protocol signaling:
   $$f_{\text{tcp\_flags}} = \frac{\sum \text{TCP Flags}}{\text{Total Packets} + \epsilon}$$
   - Highly sensitive to reconnaissance scans (FIN, XMAS, NULL) and incomplete three-way handshakes.

3. **Log Packet Length Mean ($f_{\text{log\_mean}}$)**:
   Stabilized flow payload central tendency:
   $$f_{\text{log\_mean}} = \ln(1 + \mu_{\text{pkt}})$$

4. **Log Packet Length Maximum ($f_{\text{log\_max}}$)**:
   Stabilized flow payload upper bound:
   $$f_{\text{log\_max}} = \ln(1 + \max_{\text{pkt}})$$

---

## 3. Resolution Scaling Probes (ARGUS-6, ARGUS-8, and Native-70)

To test whether cross-domain transfer performance scales monotonically with representation dimensionality, two extended common representations and an in-domain ceiling were formulated:

### ARGUS-6 (6 Features)
Extends ARGUS-4 with bidirectional temporal and volumetric properties:
- $f_5 = \ln(1 + \text{Flow Duration})$
- $f_6 = \ln(1 + \text{Byte Transfer Rate})$

### ARGUS-8 (8 Features)
Further extends ARGUS-6 with forward and reverse packet count ratios:
- $f_7 = \frac{\text{Forward Packets}}{\text{Total Packets} + \epsilon}$
- $f_8 = \frac{\text{Reverse Bytes}}{\text{Total Bytes} + \epsilon}$

### SCADA Native-70 (70 Features)
- **Role**: In-Domain Ceiling ($\text{Ceiling}_{\text{native}}$).
- Contains full protocol-specific ASDU commands, timing jitter, and industrial analog state variables.
- Models trained directly on Native-70 within D3 represent the upper performance boundary of what the data can support, not a transfer result.

---

## 4. Empirical Resolution Findings

The empirical results in Table V refute the hypothesis that representation scaling is smooth:

| Representation | Dimensions | Unique Test Tuples | Test ROC-AUC | Test F1 | Test MCC | Empirical Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **ARGUS-4** | 4 | 1,388 | 0.6262 ± 0.0001 | 0.4240 ± 0.0000 | 0.2258 ± 0.0001 | **Stable Cross-Domain Anchor** |
| **ARGUS-6** | 6 | 154,552 | 0.6534 ± 0.0002 | 0.4272 ± 0.0004 | 0.2327 ± 0.0004 | Modest gain from flow duration |
| **ARGUS-8** | 8 | 154,552 | 0.6536 ± 0.0001 | 0.4273 ± 0.0004 | 0.2328 ± 0.0003 | **Plateau**: Forward/reverse fields add zero gain |
| **Native-70** | 70 | 178,938 | **0.6739 ± 0.0004** | **0.4348 ± 0.0002** | **0.2489 ± 0.0002** | **Native SCADA Ceiling** |

*Takeaway*: Compact representations capture coarse volumetric attacks, but cannot resolve subtle protocol-level anomalies without full native protocol telemetry.
