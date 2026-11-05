import json

with open("src/argus/registry/model_registry.py", "r") as f:
    content = f.read()

# Add status fields to MODEL_METADATA
# model_d1_baseline -> planned (unverified)
content = content.replace(
    '"target_domain": "ciciot",',
    '"target_domain": "ciciot",\n        "status": "planned",'
)

# Exception for model_d2_coral (verified)
content = content.replace(
    '"target_domain": "nfton",\n        "provenance"',
    '"target_domain": "nfton",\n        "status": "verified",\n        "provenance"'
)

# Exception for model_d3_native (partial)
content = content.replace(
    '"target_domain": "iec104",\n        "provenance"',
    '"target_domain": "iec104",\n        "status": "partial",\n        "provenance"'
)

# Exception for xgb_source (planned - missing from CSV)
content = content.replace(
    '"target_domain": "ciciot",\n        "status": "planned",\n        "provenance": {\n            "training_dataset": "CICIoT2023 Train (5.49M)",\n            "adaptation_method": "NONE",\n            "features": HARMONIZED_FEATURES,\n            "training_date": "2026-08-19",\n        }\n    },\n    "xgb_adapted"',
    '"target_domain": "ciciot",\n        "status": "planned",\n        "provenance": {\n            "training_dataset": "CICIoT2023 Train (5.49M)",\n            "adaptation_method": "NONE",\n            "features": HARMONIZED_FEATURES,\n            "training_date": "2026-08-19",\n        }\n    },\n    "xgb_adapted"'
)
# Note: Since target_domain ciciot is used for xgb_source too, it gets "planned" automatically from the first replace. Let's just do it manually to be safe.
