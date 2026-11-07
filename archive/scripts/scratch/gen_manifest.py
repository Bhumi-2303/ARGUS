import json

manifest = {
    "collection_status": "Partial TON_IoT collection obtained from publicly available sources/mirrors.",
    "missing_components": [
        "SecurityEvents_GroundTruth_datasets"
    ],
    "datasets": [
        {
            "dataset_name": "TON_IoT_Processed_IoT",
            "modality": "IoT Telemetry",
            "source": "HuggingFace (SilverDragon9/UNSW_TON-IoT_Train_Test_IoT_Datasets) / Kaggle (medworldmed/ton-iot-datasets)",
            "original_filename": "IoT_*.csv",
            "local_path": "data/ton_iot/processed/Processed_IoT_dataset/",
            "row_count": "Varies per sensor (e.g., 500,000+ total)",
            "feature_count": "Varies per sensor (e.g., 6 to 12)",
            "timestamp_column": ["date", "time"],
            "label_column": ["label", "type"],
            "time_range": "2019-03-31 12:36:52 to 2019-04-29 23:59:58",
            "sha256": "Multiple (refer to TON_IOT_AUTHENTICITY_AUDIT.md)",
            "provenance_status": "Verified authentic structure",
            "experiment_readiness": "READY"
        },
        {
            "dataset_name": "TON_IoT_Network_Timestamped",
            "modality": "Network",
            "source": "Kaggle (mohammedaddoun/ton-iot)",
            "original_filename": "Network_dataset.csv (Split 1 of 23)",
            "local_path": "data/ton_iot/network_timestamped/Network_dataset_1.csv",
            "row_count": 7240, 
            "feature_count": 47,
            "timestamp_column": "ts",
            "label_column": ["label", "type"],
            "time_range": "2019-04-02 09:45:58 to 2019-04-02 12:57:32",
            "sha256": "c6797a448061f33c8b68381317ebbbca1b530d4bf3ff5f14ff1df88de06f6902",
            "provenance_status": "Partial sample verified for structure",
            "experiment_readiness": "READY WITH CAVEAT (Only partial download available locally)"
        }
    ]
}

with open('data/ton_iot/metadata/TON_IOT_FINAL_MANIFEST.json', 'w') as f:
    json.dump(manifest, f, indent=4)
