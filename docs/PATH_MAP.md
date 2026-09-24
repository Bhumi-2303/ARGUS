# Path Mapping (Restructuring)

The following datasets have been relocated to strictly enforce read-only raw data structures. Hardcoded provenance manifests (e.g. `TON_IOT_MANIFEST.json`, `SOURCES.md`) have deliberately NOT been edited to preserve their historical integrity.

Please use this map to resolve any legacy paths:

| Old Path | New Path | Type |
|---|---|---|
| `data/cic_iot_2023/` | `data/raw/cic_iot_2023/` | Dataset |
| `data/nf_ton_iot/` | `data/raw/nf_ton_iot/` | Dataset |
| `data/ton_iot/` | `data/raw/ton_iot/` | Dataset |
| `data/hai/` | `data/raw/hai/` | Dataset |
| `data/bot_iot/` | `data/raw/bot_iot/` | Dataset |

*Note: Scripts that read legacy manifests (e.g., `audit_ton_iot.py`) must dynamically apply this prefix remap (`data/` -> `data/raw/`) if reading the files.*
