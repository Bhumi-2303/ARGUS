# TON_IoT Dataset Authenticity Audit

## 1. Current dataset source
The current files were obtained from public mirrors (HuggingFace and Kaggle) rather than directly from the original UNSW CloudStor distribution (which is no longer available). They should be treated as TON_IoT subsets or TON_IoT-derived mirrors.

## 2. Files currently available
| Expected component | Present? | Status |
|--------------------|----------|--------|
| Train/Test Network | PRESENT | READY WITH CAVEAT |
| Train/Test IoT | PRESENT | READY WITH CAVEAT |
| Train/Test Linux | PRESENT | READY WITH CAVEAT |
| Train/Test Windows | PRESENT | READY WITH CAVEAT |
| Processed IoT | PRESENT | READY WITH CAVEAT |
| Processed Network | MISSING | NOT AVAILABLE |
| Processed Linux | MISSING | NOT AVAILABLE |
| Processed Windows | MISSING | NOT AVAILABLE |
| Description/Stats | MISSING | NOT AVAILABLE |
| Security Ground Truth | MISSING | NOT AVAILABLE |
| Raw Telemetry | MISSING | NOT AVAILABLE |
| Raw Network/PCAP | MISSING | NOT AVAILABLE |
| Raw Linux | MISSING | NOT AVAILABLE |
| Raw Windows | MISSING | NOT AVAILABLE |

## 3. Files missing
- Processed Network, Linux, Windows datasets
- Description_stats_datasets
- SecurityEvents_GroundTruth_datasets
- All raw datasets (PCAP, raw telemetry, etc.)

## 4. File-by-file provenance

### IoT_Fridge.csv
- **Local path:** data/ton_iot/processed/Processed_IoT_dataset/IoT_Fridge.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 24965618 bytes
- **SHA256:** e5c7fd42c1d44898eb8afe6800d7a335a38a6a8394c6af083407b9f581736272
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### IoT_GPS_Tracker.csv
- **Local path:** data/ton_iot/processed/Processed_IoT_dataset/IoT_GPS_Tracker.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 31423494 bytes
- **SHA256:** aa1146435bd964b7d247736d5c8a12221b0e9d16734d33f80b7e7a8153ebe917
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### IoT_Garage_Door.csv
- **Local path:** data/ton_iot/processed/Processed_IoT_dataset/IoT_Garage_Door.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 25760262 bytes
- **SHA256:** 76639fd3e4b5a800d7e3216aefc6398c11a3f87a6b3bfcebf3f2a893f135e204
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### IoT_Modbus.csv
- **Local path:** data/ton_iot/processed/Processed_IoT_dataset/IoT_Modbus.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 15347014 bytes
- **SHA256:** 1cdb245661db3f15be52c3e8aeba5b1a3af37b8eed3f9132a7f1a03d8111aa16
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### IoT_Motion_Light.csv
- **Local path:** data/ton_iot/processed/Processed_IoT_dataset/IoT_Motion_Light.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 16561568 bytes
- **SHA256:** 6bdd41ac3c3e9fc2e70766691db000a063c73cbc85be7d5f6ce17a4d66dc346e
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### IoT_Thermostat.csv
- **Local path:** data/ton_iot/processed/Processed_IoT_dataset/IoT_Thermostat.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 19046111 bytes
- **SHA256:** abb919eb3816d30036ad54bfd65bbbdf1e7b527bdb2993c22d9a36a21aa3a5c2
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### IoT_Weather.csv
- **Local path:** data/ton_iot/processed/Processed_IoT_dataset/IoT_Weather.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 42002630 bytes
- **SHA256:** 1b5e379011d37a1b4bf3598f3c06eb554b207a30787ddcb6a30833092c6ca9a1
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_Test_IoT_Fridge.csv
- **Local path:** data/ton_iot/train_test/Train_Test_IoT_dataset/Train_Test_IoT_Fridge.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 1678744 bytes
- **SHA256:** 56377a00b97204ea65f8912eadea9e626fe05d091f975f5be64c94c85efe3149
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_Test_IoT_Garage_Door.csv
- **Local path:** data/ton_iot/train_test/Train_Test_IoT_dataset/Train_Test_IoT_Garage_Door.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 1739414 bytes
- **SHA256:** 44b2d63f233ed239d604815f53e2b2ba6ec2b9bc604a9f6fbed6b98d55e53188
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_Test_IoT_GPS_Tracker.csv
- **Local path:** data/ton_iot/train_test/Train_Test_IoT_dataset/Train_Test_IoT_GPS_Tracker.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 2122967 bytes
- **SHA256:** 71c6cc302b14822aea699cf41a02dad36089ea59b87a28000b38a44b2d23cb9b
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_Test_IoT_Modbus.csv
- **Local path:** data/ton_iot/train_test/Train_Test_IoT_dataset/Train_Test_IoT_Modbus.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 1694191 bytes
- **SHA256:** 78345a857244e671b0c255ca65aac619049632448fc5aa736f1cea255f308cbb
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_Test_IoT_Motion_Light.csv
- **Local path:** data/ton_iot/train_test/Train_Test_IoT_dataset/Train_Test_IoT_Motion_Light.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 1469248 bytes
- **SHA256:** e0e145ff3d8145d4ad713380a291248dba74e75a70bd75525719ffaaaf2f5242
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_Test_IoT_Thermostat.csv
- **Local path:** data/ton_iot/train_test/Train_Test_IoT_dataset/Train_Test_IoT_Thermostat.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 1464768 bytes
- **SHA256:** b475654a43ec885fd8c3409d9e85b7902ecc3ad47440948466f4fe3559fd1f6d
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_Test_IoT_Weather.csv
- **Local path:** data/ton_iot/train_test/Train_Test_IoT_dataset/Train_Test_IoT_Weather.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 2587701 bytes
- **SHA256:** 10c49fe8a6eae98db688e277e96218c9a9bf587cc5aee5962833470366dafdba
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_test_linux_disk.csv
- **Local path:** data/ton_iot/train_test/Train_Test_Linux_dataset/Train_test_linux_disk.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 2987385 bytes
- **SHA256:** 6116cd5d3a7c7bf1926a55fadd6a447255be29895b88da17bfdcb0431f5fea2f
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_test_linux_memory.csv
- **Local path:** data/ton_iot/train_test/Train_Test_Linux_dataset/Train_test_linux_memory.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 3530080 bytes
- **SHA256:** cfa9b8f32e4a1ba0974dcdd1f561ba60e0071344a59215d9479eaa640626dc31
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_Test_Linux_process.csv
- **Local path:** data/ton_iot/train_test/Train_Test_Linux_dataset/Train_Test_Linux_process.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 4900281 bytes
- **SHA256:** 63a878f944bea1d3347da7335833738d3e616fe3db41157330d3bb0dc3f23f7e
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### train_test_network.csv
- **Local path:** data/ton_iot/train_test/Train_Test_Network_dataset/train_test_network.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 29902775 bytes
- **SHA256:** 26ddc513552de36de6428b2e578efaed2b57504c716dfba847cc0109a64e1974
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_Test_Windows_10.csv
- **Local path:** data/ton_iot/train_test/Train_Test_Windows_dataset/Train_Test_Windows_10.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 21769739 bytes
- **SHA256:** 85f0827697ef5b0faf76a8b41371e95fd5e6ea3950d19ea35a9d7f35042703a8
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

### Train_Test_Windows_7.csv
- **Local path:** data/ton_iot/train_test/Train_Test_Windows_dataset/Train_Test_Windows_7.csv
- **Source:** Mirror (HuggingFace/Kaggle)
- **Size:** 14070171 bytes
- **SHA256:** 5ed0c685148449bb493dd4196a35fcf0d1dc82d0a50b66da84a34114be36ef1d
- **Classification:** Mirror copy with apparently unchanged contents
- **Evidence:** Column headers correspond to expected TON_IoT features. Values look normal.
- **Caveats:** Mirror source, original checksum unavailable.

## 5. Dataset structure comparison
The current local structure contains the `Train_Test_datasets` (Network, IoT, Linux, Windows) and a subset of `Processed_datasets` (IoT only). The raw folders, ground truth folders, and description stats are completely missing.

## 6. Label analysis
| File | Label column | Number of classes | Classes | Samples |
|------|--------------|-------------------|---------|---------|
| IoT_Fridge.csv | label | 2 | ['0', '1'] | 587076 |
| IoT_GPS_Tracker.csv | label | 2 | ['0', '1'] | 595686 |
| IoT_Garage_Door.csv | label | 2 | ['0', '1'] | 591446 |
| IoT_Modbus.csv | label | 2 | ['0', '1'] | 287194 |
| IoT_Motion_Light.csv | label | 2 | ['0', '1'] | 452262 |
| IoT_Thermostat.csv | label | 2 | ['0', '1'] | 442228 |
| IoT_Weather.csv | label | 2 | ['0', '1'] | 650242 |
| Train_Test_IoT_Fridge.csv | label | 2 | ['1', '0'] | 39944 |
| Train_Test_IoT_Garage_Door.csv | label | 2 | ['1', '0'] | 39587 |
| Train_Test_IoT_GPS_Tracker.csv | label | 2 | ['1', '0'] | 38960 |
| Train_Test_IoT_Modbus.csv | label | 2 | ['1', '0'] | 31106 |
| Train_Test_IoT_Motion_Light.csv | label | 2 | ['1', '0'] | 39488 |
| Train_Test_IoT_Thermostat.csv | label | 2 | ['1', '0'] | 32774 |
| Train_Test_IoT_Weather.csv | label | 2 | ['1', '0'] | 39260 |
| Train_test_linux_disk.csv | attack | 2 | ['1', '0'] | 90112 |
| Train_test_linux_memory.csv | label | 2 | ['1', '0'] | 70112 |
| Train_Test_Linux_process.csv | label | 2 | ['1', '0'] | 90112 |
| train_test_network.csv | label | 2 | ['1', '0'] | 211043 |
| Train_Test_Windows_10.csv | label | 2 | ['1', '0'] | 21104 |
| Train_Test_Windows_7.csv | label | 2 | ['0', '1'] | 15980 |

## 7. Timestamp analysis
**IoT_Fridge.csv**
- Column: date
- Min: 1-Apr-19
- Max: 4-Apr-19
- Unique: 13
- Missing: 0
- Monotonic: False

**IoT_GPS_Tracker.csv**
- Column: date
- Min: 1-Apr-19
- Max: 4-Apr-19
- Unique: 13
- Missing: 0
- Monotonic: False

**IoT_Garage_Door.csv**
- Column: date
- Min: 1-Apr-19
- Max: 4-Apr-19
- Unique: 13
- Missing: 21335
- Monotonic: False

**IoT_Modbus.csv**
- Column: date
- Min: 1-Apr-19
- Max: 4-Apr-19
- Unique: 13
- Missing: 0
- Monotonic: False

**IoT_Motion_Light.csv**
- Column: date
- Min: 1-Apr-19
- Max: 4-Apr-19
- Unique: 12
- Missing: 0
- Monotonic: False

**IoT_Thermostat.csv**
- Column: date
- Min: 1-Apr-19
- Max: 4-Apr-19
- Unique: 12
- Missing: 4621
- Monotonic: False

**IoT_Weather.csv**
- Column: date
- Min: 1-Apr-19
- Max: 4-Apr-19
- Unique: 13
- Missing: 0
- Monotonic: False

**Train_Test_IoT_Fridge.csv**
- Column: date
- Min: 1-Apr-19
- Max: 31-Mar-19
- Unique: 8
- Missing: 0
- Monotonic: False

**Train_Test_IoT_Garage_Door.csv**
- Column: date
- Min: 1-Apr-19
- Max: 31-Mar-19
- Unique: 8
- Missing: 0
- Monotonic: False

**Train_Test_IoT_GPS_Tracker.csv**
- Column: date
- Min: 1-Apr-19
- Max: 31-Mar-19
- Unique: 7
- Missing: 0
- Monotonic: False

**Train_Test_IoT_Modbus.csv**
- Column: date
- Min: 23-Apr-19
- Max: 31-Mar-19
- Unique: 6
- Missing: 0
- Monotonic: False

**Train_Test_IoT_Motion_Light.csv**
- Column: date
- Min: 1-Apr-19
- Max: 31-Mar-19
- Unique: 7
- Missing: 0
- Monotonic: False

**Train_Test_IoT_Thermostat.csv**
- Column: date
- Min: 1-Apr-19
- Max: 31-Mar-19
- Unique: 8
- Missing: 0
- Monotonic: False

**Train_Test_IoT_Weather.csv**
- Column: date
- Min: 23-Apr-19
- Max: 31-Mar-19
- Unique: 6
- Missing: 0
- Monotonic: False

**Train_Test_Windows_10.csv**
- Column: Processor_pct_ Idle_Time
- Min:  
- Max: 99.63895633
- Unique: 21021
- Missing: 0
- Monotonic: False

**Train_Test_Windows_7.csv**
- Column: Processor(_Total) pct_ Idle Time
- Min:  
- Max: 99.94958249
- Unique: 3170
- Missing: 0
- Monotonic: False


## 8. Duplication/data leakage analysis
- **IoT_Fridge.csv**: 100863 duplicate rows found.
- **IoT_GPS_Tracker.csv**: 25320 duplicate rows found.
- **IoT_Garage_Door.csv**: 393927 duplicate rows found.
- **IoT_Modbus.csv**: 0 duplicate rows found.
- **IoT_Motion_Light.csv**: 228967 duplicate rows found.
- **IoT_Thermostat.csv**: 35052 duplicate rows found.
- **IoT_Weather.csv**: 26045 duplicate rows found.
- **Train_Test_IoT_Fridge.csv**: 2834 duplicate rows found.
- **Train_Test_IoT_Garage_Door.csv**: 20221 duplicate rows found.
- **Train_Test_IoT_GPS_Tracker.csv**: 0 duplicate rows found.
- **Train_Test_IoT_Modbus.csv**: 13314 duplicate rows found.
- **Train_Test_IoT_Motion_Light.csv**: 13658 duplicate rows found.
- **Train_Test_IoT_Thermostat.csv**: 424 duplicate rows found.
- **Train_Test_IoT_Weather.csv**: 0 duplicate rows found.
- **Train_test_linux_disk.csv**: 66480 duplicate rows found.
- **Train_test_linux_memory.csv**: 51949 duplicate rows found.
- **Train_Test_Linux_process.csv**: 73591 duplicate rows found.
- **train_test_network.csv**: 20569 duplicate rows found.
- **Train_Test_Windows_10.csv**: 0 duplicate rows found.
- **Train_Test_Windows_7.csv**: 0 duplicate rows found.

## 9. Modification/processing analysis
All files are classified as **Mirror copies with apparently unchanged contents** based on standard row counts and columns. They are derived from mirrors and not the original server.

## 10. Research suitability
The datasets are **READY WITH CAVEAT** for in-domain experiments. For multi-agent or cross-domain experiments, the lack of a unifying ground truth timeline (`SecurityEvents_GroundTruth_datasets`) makes temporal alignment across modalities extremely challenging and potentially unsafe.

## 11. Missing components
- SecurityEvents_GroundTruth
- Description_stats
- raw PCAP
- raw telemetry
- raw Linux/Windows
- processed Network/Linux/Windows
