# Representation Definition & Dimensionality Report

**Audit Date**: August 22, 2026

---

## 1. ARGUS-4 Harmonized Representation
The ARGUS-4 representation consists of 4 cross-domain aligned features:
1. : Ratio of mean to maximum packet payload size ($	ext{Pkt Len Mean} / (	ext{Pkt Len Max} + 10^{-10})$)
2. : Sum / multiplicity of active TCP control flags
3. : $\ln(1 + \max(0, 	ext{Pkt Len Mean}))$
4. : $\ln(1 + \max(0, 	ext{Pkt Len Max}))$

## 2. Native SCADA (Native-73) Representation
The Native SCADA representation consists of the 73 full flow features extracted by CICFlowMeter from the raw IEC 60870-5-104 telemetry ().
- **Nominal Feature Count**: 73 numeric flow statistics
- **Effective Non-Constant Dimensions**: 70 active non-zero variance features on target D3
- **Terminology Rule**: Referred to as  (or ) throughout all experimental manifests, figures, and tables, preserving consistency with .
