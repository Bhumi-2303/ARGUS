# ARGUS NR-04: Strict Preprocessing Audit Report

**Audit Date**: 2026-08-25 21:12:44  
**Status**: **PASSED (ZERO LEAKAGE PREPROCESSING)**  

---

## 1. Feature Representation Specification (70 Features)
- **Raw Features**: Flow duration, packet length statistics (min, max, mean, std), inter-arrival times (IAT), subflow counts, TCP window sizes, header lengths, and active/idle intervals.
- **Handling of Special Values**: `np.inf` and `-np.inf` replaced with `np.nan`, followed by `fillna(0)`.
- **Scaling Protocol**: `StandardScaler` mean and standard deviation parameters fitted **exclusively on the training partition**.
- **Test Set Treatment**: Frozen test partition transformed strictly via `scaler.transform()`. No test statistics computed or utilized.

## 2. Model Input Dimensions
- Total Input Dimensions: **66**
- Feature Tokenizer Mapping: 70 numeric flow features mapped to embedding tokens.
