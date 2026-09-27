# Group-Token Transformer Specification (V2 Exploratory)

This specification defines the input architecture for a group-token transformer, mapping raw dataset variables from `SCHEMA_AUDIT.md` into distinct, semantically cohesive feature tokens.

## 1. Token Group Definitions
Based on the universal canonical mapping, we split the raw network features into 5 distinct tokens per flow. This groups highly correlated features together and segregates known leaky/fragile features (like timing) into their own tokens, allowing the transformer's attention heads to dynamically weight or drop them.

*   **Token 1: Size Group** (`log_pkt_mean`, `log_pkt_max`, `pkt_mean_to_max`)
    *   *Source:* Derived from `Total Bytes` and `Total Packets`.
    *   *Status:* Safely Common.
*   **Token 2: Volumetric Group** (`log_total_pkts`, `log_total_bytes`)
    *   *Source:* Derived from `Total Packets` and `Total Bytes`.
    *   *Status:* Safely Common.
*   **Token 3: Protocol Group** (`protocol_embed`, `tcp_flag_density`)
    *   *Source:* Derived from categorical `Protocol` and TCP flag counts/strings.
    *   *Status:* Safely Common.
*   **Token 4: Directional Group** (`fwd_pkt_ratio`, `fwd_byte_ratio`)
    *   *Source:* Derived from `Fwd/Bwd Packets` and `Fwd/Bwd Bytes`.
    *   *Status:* Dataset-Specific (Missing in CICIoT2023).
*   **Token 5: Timing Group** (`log_duration`, `log_byte_rate`)
    *   *Source:* Derived from `Flow Duration` and `Total Bytes`.
    *   *Status:* Derivable-but-not-direct (Requires derivation via IAT/Rate in CICIoT, natively present in others).

## 2. Per-Domain Presence Table
Tokens are constructed strictly based on `SCHEMA_AUDIT.md` field availability. No missing features are silently imputed.

| Dataset | Token 1 (Size) | Token 2 (Volumetric) | Token 3 (Protocol) | Token 4 (Directional) | Token 5 (Timing) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CICIoT2023** | Present | Present | Present | **Masked-Absent** | Present (Derived) |
| **NF-ToN-IoT-v2** | Present | Present | Present | Present | Present |
| **BoT-IoT** | Present | Present | Present | Present | Present |
| **TON_IoT** | Present | Present | Present | Present | Present |

## 3. Masking Mechanism
**Mechanism: Zero-Vector Input + Boolean Attention Mask.**

*   *Implementation:* When a token is absent (e.g., Token 4 for CICIoT2023), its raw input vector is populated with exact zeros, and its corresponding entry in the boolean `attention_mask` is set to `0` (False).
*   *Justification:* We actively reject using a learned `[MISSING]` mask embedding. If we used a learned embedding for missing tokens, the embedding itself would serve as a constant bias vector injected into the sequence. Since Token 4 is *only* missing in CICIoT2023, a learned `[MISSING]` embedding would become a perfect, trivially identifiable domain signature for CICIoT. By using a strict attention mask, the transformer simply computes self-attention over a sequence of length 4 instead of 5, preventing the "absence" from routing active signal into the `[CLS]` token.

## 4. Embedding Scheme
*   **Continuous Features:** Each group $g$ contains a small vector of continuous features $x_g \in \mathbb{R}^{d_g}$. This is passed through a per-group linear projection $W_g x_g + b_g \in \mathbb{R}^{d_{model}}$.
*   **Categorical Features:** The categorical `protocol` identity in Token 3 is passed through an embedding lookup $E_{proto}(protocol)$ and concatenated with `tcp_flag_density` before its linear projection.
*   **Token Identification:** Because the sequence is an unordered set of heterogeneous groups, we add a learned "Group-Type Positional Embedding" (e.g., $P_{Size}, P_{Volumetric}$) to each projected token so the model knows which semantic group a token represents.
*   **Strict Isolation:** No target labels (Attack/Benign), attack categories, or domain tags are provided to the input embeddings or the attention mechanism at any stage.

## 5. Known Risks & Vulnerabilities
Before moving to implementation, we explicitly flag the following architectural risks which must be tested:

1.  **Domain Leakage via Sequence Length (The Masking Artifact):** Even with attention masking, the fact that CICIoT2023 flows always have 4 tokens and NF-ToN/BoT-IoT flows always have 5 tokens creates a sequence-length discrepancy. The transformer might learn to count the number of attended tokens, indirectly realizing that `seq_len == 4` implies the CICIoT domain.
2.  **Domain Leakage via the Timing Token:** As proven in the V1.5 validation report, timing/rate profiles (Token 5) are intrinsically distinct between CICIoT and NF-ToN (99.9% separability). By explicitly isolating Timing into Token 5, we expect the attention heads to strongly latch onto Token 5 to cheat the domain. We will need to monitor attention weights to see if it drops the token or abuses it.
3.  **BoT-IoT Token Degeneracy:** On BoT-IoT flood traffic, Token 1 (Size), Token 2 (Volumetric), and Token 5 (Timing) will still collapse into highly dense, uniform buckets. The transformer might overfit to the exact constant values embedded in these tokens for BoT-IoT records, inflating baseline metrics artificially.
