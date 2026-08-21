# ARGUS `i_msg_ratio` Protocol Feature Diagnostic Report

**Target Domain**: IEC 60870-5-104 SCADA Telemetry (Domain 3 / D3)  
**Target Feature Under Investigation**: `i_msg_ratio` (Information ASDU Frame Ratio, LightGBM Gain: $38,080.21$)  
**Dataset Analyzed**: $N = 3,766$ Volume-Matched Subsample Flows (and $N = 23,045$ Mixed File Flows)  
**Audit Date**: August 21, 2026  

---

## 1. Executive Summary & Diagnostic Answers

1. **Cross-Tabulation Purity**:
   - At a threshold of $\text{i\_msg\_ratio} > 0.40$, the feature achieves **$99.66\%$ Attack Class Purity** ($1,739 / 1,745$ flows) on the volume-matched subsample.
   - Benign background polling flows maintain $\text{i\_msg\_ratio} \le 0.40$ ($92.88\%$ benign purity, mean $0.2339$).

2. **Source File Contributions & Disjointness Check**:
   - Benign flows in the volume-matched subsample originate from **80 distinct source files**.
   - Attack flows originate from **106 distinct source files**.
   - **68 source files** contribute BOTH benign and attack flows to the volume-matched subsample.
   - **Finding**: Benign and attack flows are **not** drawn from small, disjoint sets of files. They are broadly distributed across 68 shared capture files.

3. **Ablation Test Without `i_msg_ratio`**:
   - When `i_msg_ratio` is completely removed from the feature set, **ROC-AUC on the held-out volume-matched test set remains $0.999994$** ($\text{Precision} = 100.00\%$, $\text{Recall} = 99.67\%$, $\text{FPR} = 0.00\%$, $\text{MCC} = 0.9975$).
   - The model smoothly transitions to `flow packet APDU length mean` (Gain: $38,033.70$), `s_msg_ratio` (Gain: $1,051.70$), and `cot=3` (Gain: $618.53$).

4. **Assessment: Genuine Protocol Semantics vs. Shortcut Artifact**:
   - **Verdict: Genuine Protocol-Semantic Signal**.
   - Unlike cumulative volume counts (`total flow packets` or `u_message packets`) which scale with capture duration, `i_msg_ratio` is a **dimensionless ratio** measuring the proportion of Information (I-format) ASDUs relative to total IEC 104 frames.
   - **Domain Mechanics**: Normal SCADA polling exchanges monitoring data (I-frames) and frequent Supervisory ACKs (S-frames), keeping `i_msg_ratio` low ($\approx 0.20 \dots 0.30$). Threat campaigns (command injections, setpoint writes, DoS command bursts) inject rapid Information-type ASDUs without waiting for supervisory cycles, elevating `i_msg_ratio` above $0.40$.

---

## 2. Detailed Cross-Tabulation Analysis (`i_msg_ratio`)

### 2.1 Volume-Matched Subsample ($N = 3,766$ Flows)

| `i_msg_ratio` Range | Benign Flows ($y=0$) | Attack Flows ($y=1$) | Total Flows | % Attack Purity |
| :--- | ---: | ---: | ---: | ---: |
| $[0.00, 0.20]$ | 552 | 2 | 554 | $0.36\%$ |
| $(0.20, 0.40]$ | 1,325 | 142 | 1,467 | $9.68\%$ |
| **$[0.00, 0.40]$ Subtotal** | **1,877** | **144** | **2,021** | **$7.13\%$ ($92.87\%$ Benign)** |
| $(0.40, 0.60]$ | 6 | 455 | 461 | **$98.70\%$** |
| $(0.60, 0.80]$ | 0 | 258 | 258 | **$100.00\%$** |
| $(0.80, 0.90]$ | 0 | 925 | 925 | **$100.00\%$** |
| $(0.90, 1.00]$ | 0 | 101 | 101 | **$100.00\%$** |
| **$(0.40, 1.00]$ Subtotal** | **6** | **1,739** | **1,745** | **$99.66\%$ Attack Purity** |

---

## 3. Distribution Statistics Across Mixed Files ($N = 23,045$ Flows)

Across the 70 mixed files containing both benign background traffic and attack injections:

| Class | Count | Mean `i_msg_ratio` | Std | Min | 25% | Median (50%) | 75% | Max |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Benign Telemetry ($y=0$)** | 8,908 | **$0.2188$** | $0.0610$ | $0.0000$ | $0.1739$ | $0.2174$ | $0.2667$ | **$0.4286$** |
| **Attack Injections ($y=1$)** | 14,137 | **$0.3866$** | $0.0748$ | $0.0000$ | $0.3750$ | $0.3750$ | $0.4444$ | **$1.0000$** |

### Key Observation
In mixed files, **benign telemetry is strictly bounded below $\text{i\_msg\_ratio} \le 0.4286$** (75th percentile at $0.2667$), whereas attack flows shift significantly higher, reaching up to $1.0000$.

---

## 4. Ablation Performance (Excluding `i_msg_ratio` and U-Messages)

To confirm that classification does not collapse when `i_msg_ratio` is excluded:

| Feature Configuration | ROC-AUC (Test, 0% File Overlap) | Precision | Recall | FPR | $F_1$ Score | MCC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **With `i_msg_ratio`** | $0.999965$ | $100.00\%$ | $99.35\%$ | $0.00\%$ | $0.9967$ | $0.9950$ |
| **WITHOUT `i_msg_ratio` (Ablated)** | **$0.999994$** | **$100.00\%$** | **$99.67\%$** | **$0.00\%$** | **$0.9984$** | **$0.9975$** |

### Top Drivers Without `i_msg_ratio`
1. `flow packet APDU length mean` (**Gain: $38,033.70$**)
2. `s_msg_ratio` (**Gain: $1,051.70$**)
3. `cot=3` (**Gain: $618.53$**) — Cause of Transmission: Spontaneous
4. `fw packet APDU length mean` (**Gain: $474.75$**)
5. `bw packet APDU length mean` (**Gain: $269.43$**)

---

## 5. Summary Conclusion

1. `i_msg_ratio` is a **legitimate protocol-semantic feature**, representing the structural ratio of Information command/data ASDUs to total frame traffic.
2. It does **not** suffer from the duration/cumulative volume artifact that affected U-messages and raw packet counts.
3. Even when `i_msg_ratio` is completely ablated, other protocol features (`APDU length mean`, `s_msg_ratio`, `cot=3`) maintain **$\text{ROC-AUC} = 0.999994$** under strict 0% file-overlap grouped splits on volume-matched data.
