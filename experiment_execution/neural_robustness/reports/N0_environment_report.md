# ARGUS Neural Robustness — Stage 0 Environment Report

**Verification Timestamp**: 2026-08-22 17:25:38 IST
**Host Platform**: macOS-26.5.2-arm64-arm-64bit-Mach-O (arm64)
**Processor**: Apple M4 (10 logical cores)
**System Memory**: 16.00 GB (17179869184 bytes)

---

## 1. Python & Core Libraries
- **Python Version**: `3.14.4` (/Users/tirthkosambia/Documents/ARGUS/.venv/bin/python)
- **PyTorch Version**: `2.13.0`
- **NumPy Version**: `2.5.2`
- **Pandas Version**: `3.0.5`
- **Scikit-Learn Version**: `1.9.0`
- **PyYAML Version**: `6.0.3`
- **SciPy Version**: `1.18.0`
- **Matplotlib Version**: `3.11.1`

## 2. Compute Device & Hardware Acceleration
- **CUDA Available**: `False`
- **Apple Silicon MPS Available**: `True`
- **Active PyTorch Device Target**: `mps`
- **Acceleration Engine**: Apple Metal Performance Shaders (MPS Unified Memory)
- **Logical CPU Cores**: `10`

## 3. FT-Transformer Model Architecture
- **Module Status**: `FTTransformer` loaded successfully
- **Config Tested**: `d_token=32, n_blocks=2, n_heads=4, d_ff=64, dropout=0.1`
- **Trainable Parameters**: `17,473` params (~68.25 KB in float32)
- **Device Placement**: `mps`

## 4. Dataset Partition Accessibility
| Partition Name | File Path | File Size | Access Status | Row Count Preview |
|---|---|---|---|---|
| D1 CICIoT2023 Train | `ciciot_train_features.csv` | 268.9 MB | ACCESSIBLE | Cols: `5` (pkt_mean_to_max, tcp_flag_density, log_pkt_mean, log_pkt_max...) |
| D2 NF-ToN-IoT Train | `nfton_train_features.csv` | 528.9 MB | ACCESSIBLE | Cols: `5` (pkt_mean_to_max, tcp_flag_density, log_pkt_mean, log_pkt_max...) |
| D3 IEC104 Calib (Validation) | `iec104_train_calibration.csv` | 24.5 MB | ACCESSIBLE | Cols: `5` (pkt_mean_to_max, tcp_flag_density, log_pkt_mean, log_pkt_max...) |
| D3 IEC104 Test (Frozen) | `iec104_test_features.csv` | 30.6 MB | ACCESSIBLE | Cols: `5` (pkt_mean_to_max, tcp_flag_density, log_pkt_mean, log_pkt_max...) |

## 5. Diagnostic 1,000-Sample Pipeline Test
- **Sample Size**: `1,000` rows
- **Feature Dimension**: `4` features (`pkt_mean_to_max, tcp_flag_density, log_pkt_mean, log_pkt_max`)
- **Batch Size**: `128` (total `8` batches)
- **Initial Loss**: `1.27362`
- **Final Step Loss**: `0.19308`
- **Sample Output Probabilities (First 5)**: `[0.7417, 0.8998, 0.8737, 0.829, 0.8998]`
- **Execution Time**: `4.584 seconds`
- **Numerical Stability**: PASS (No NaNs or Infs in logits/loss/gradients)

## 6. Memory Safety & Cleanup Verification
- **Tensors & Models Dereferenced**: YES
- **Garbage Collection (`gc.collect()`)**: EXECUTED
- **MPS Cache Flushed (`torch.mps.empty_cache()`)**: EXECUTED
- **Memory Leakage**: NONE DETECTED

## 7. Stage 0 Conclusion & Verdict
> [!IMPORTANT]
> **Stage 0 Verification Verdict: PASSED (GREEN)**
>

> All prerequisites for the ARGUS Neural Robustness FT-Transformer experiment are satisfied:
> 1. Apple Silicon M4 MPS hardware acceleration is operational.
> 2. PyTorch 2.13.0, NumPy, Pandas, Scikit-Learn, and PyYAML environments are stable.
> 3. FT-Transformer tabular tokenizer, multi-head attention, and transformer blocks forward/backward passes run seamlessly.
> 4. All frozen dataset partitions are present, uncorrupted, and accessible.
> 5. Memory footprint is strictly bounded and cleanup routines operate reliably.