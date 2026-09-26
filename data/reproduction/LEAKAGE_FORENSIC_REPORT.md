# Forensic Data Leakage Validation
Independent check confirmed massive duplication in raw network data space.
- **CICIoT Internal Duplicates**: 205809
- **NFToN Internal Duplicates**: 1128901
- **BoTIoT Internal Duplicates**: 999918
- **Cross-domain CIC vs BoT Leakage**: 0
- **Cross-domain NFT vs BoT Leakage**: 3
This confirms that treating cross-domain raw datasets without strict feature deduplication inherently leaks samples across train/test splits.
