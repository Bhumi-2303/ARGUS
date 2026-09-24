# Label Harmonization Matrix

## Binary Labels (Attack vs Benign)
All datasets natively support or trivially map to a binary `[0, 1]` classification:
*   **CICIoT2023**: Map `label == 'Benign'` to 0, else 1.
*   **NF-ToN-IoT**: `Label` (0/1) - Directly compatible.
*   **BoT-IoT**: `attack` (0/1) - Directly compatible.
*   **TON_IoT**: `label` (0/1) - Directly compatible.
*   **HAI**: `attack` (0/1) - Directly compatible.

## Multiclass Attack Categories
| Concept | CICIoT2023 | NF-ToN-IoT | BoT-IoT | TON_IoT | HAI |
|---------|------------|------------|---------|---------|-----|
| DoS / DDoS | `DDoS`, `DoS` | `dos` | `DoS`, `DDoS` | `dos`, `ddos` | N/A |
| Reconnaissance | `Recon` | `scanning` | `Reconnaissance` | `scanning` | N/A |
| Injection | `Web-based` | `injection`, `xss` | N/A | `injection`, `xss` | N/A |
| Theft / Exfiltration| `Spoofing` | `mitm` | `Theft` | `mitm` | N/A |
| Password / Brute | `BruteForce` | `password` | N/A | `password` | N/A |
| Malware / Backdoor| N/A | `backdoor`, `ransomware` | N/A | `backdoor`, `ransomware` | N/A |

*Note: HAI anomalies are physical process deviations (e.g., valve manipulation), which are "NOT DIRECTLY COMPARABLE" to IT network attack categories.*
