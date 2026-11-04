# ARGUS Developer & Operational Tools

This directory contains standalone CLI tools and utilities for development, data management, authentication, and evaluation.

## Directory Structure

```
tools/
├── auth/
│   └── generate_token.py        # Generates signed JWT authentication tokens for API testing
├── data/
│   ├── create_sample.py         # Subsets raw parquet data into balanced demo sample partitions
│   └── validate_dataset.py      # Computes checksums and validates dataset schema integrity
├── audit/
│   └── audit_ton_iot.py         # Audits NF-ToN-IoT-v2 partition distributions and feature statistics
└── evaluation/
    └── compile_multiseed.py     # Aggregates multi-seed experiment logs into statistical summaries
```

## Usage Examples

### Generate Development JWT Token
```bash
python tools/auth/generate_token.py --role Admin --expiry-hours 24
```

### Validate Dataset Integrity
```bash
python tools/data/validate_dataset.py
```
