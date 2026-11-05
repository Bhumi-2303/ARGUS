import json
import os

with open('data/FINAL_DATASET_MANIFEST.json', 'r') as f:
    manifest = json.load(f)

# Update existing elements
for item in manifest:
    if item['dataset'] == 'CICIoT2023':
        item['completeness_status'] = 'PARTIAL (1/169 splits)'
        item['known_limitations'] = 'Kaggle mirror hangs; bulk download of 3GB halted. Only first split available.'
        item['source_url'] = 'https://www.kaggle.com/datasets/madhavmalhotra/unb-cic-iot-dataset'
        item['attack_category_column'] = 'label'
    elif item['dataset'] == 'NF-ToN-IoT':
        item['completeness_status'] = 'VERIFIED COMPLETE'
        item['known_limitations'] = 'None'
        item['source_url'] = 'https://www.kaggle.com/datasets/dhoogla/nftoniot'
        item['attack_category_column'] = 'label'
    elif item['dataset'] == 'HAI':
        item['completeness_status'] = 'PARTIAL (train1.csv only)'
        item['known_limitations'] = 'Kaggle mirror hangs; Git LFS excessively slow. Only train1.csv acquired.'
        item['source_url'] = 'https://www.kaggle.com/datasets/icsdataset/hai-security-dataset'
        item['attack_category_column'] = 'Attack'

# Add TON_IoT Network
manifest.append({
    "dataset": "TON_IoT_Network",
    "version": "2019",
    "source": "Kaggle (mohammedaddoun/ton-iot)",
    "source_type": "mirror",
    "source_url": "https://www.kaggle.com/datasets/mohammedaddoun/ton-iot",
    "original_files": ["Network_dataset_1.csv"],
    "local_files": ["data/ton_iot/network_timestamped/Network_dataset_1.csv"],
    "file_count": 1,
    "size_bytes": 1048576,
    "rows": 7240,
    "features": 47,
    "timestamp_column": "ts",
    "label_column": "label",
    "attack_category_column": "type",
    "time_range": {
        "start": "2019-04-02 09:45:58",
        "end": "2019-04-02 12:57:32"
    },
    "sha256": {
        "Network_dataset_1.csv": "c6797a448061f33c8b68381317ebbbca1b530d4bf3ff5f14ff1df88de06f6902"
    },
    "provenance_status": "VERIFIED MIRROR",
    "completeness_status": "PARTIAL",
    "validation_status": "VERIFIED",
    "known_limitations": "Kaggle mirror hangs immediately after 1MB chunk. Bulk 3.2GB download failed. SecurityEvents_GroundTruth remains unavailable from all public mirrors."
})

with open('data/FINAL_DATASET_MANIFEST.json', 'w') as f:
    json.dump(manifest, f, indent=4)
