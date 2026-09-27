# V2 Group-Token Transformer (Exploratory)

This directory contains experimental work on a group-token transformer architecture for ARGUS.

## Research Protocol
Strictly separated from V1 production code. Every architectural iteration must pass through:
1. **Held-Out Protocol:** Strict train/test splits from inception.
2. **Diversity/Degeneracy Check:** Verification that the representation does not collapse on extreme distributions (e.g., BoT-IoT flood traffic).
3. **Leakage & Domain Separability Check:** Verification that the input sequence/tokens do not inherently leak domain identity (e.g., CICIoT vs NF-ToN vs BoT-IoT).
4. **GO/NO-GO Checkpoints:** Explicit evaluation before heavy training investment.

**Status:** INCEPTION
