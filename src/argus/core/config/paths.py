import os
from pathlib import Path

# 1. Determine the root directory reliably based on this script's location
# This file is at src/argus/core/config/paths.py, so root is 4 levels up
_current_dir = Path(__file__).resolve().parent
PROJECT_ROOT = _current_dir.parent.parent.parent.parent

# 2. Data Root Resolution
# Order: Environment Variable -> Repository relative default
_env_data_root = os.getenv("ARGUS_DATA_ROOT")
if _env_data_root:
    DATA_ROOT = Path(_env_data_root).resolve()
else:
    DATA_ROOT = PROJECT_ROOT / "data"

# Dataset-specific paths
class DatasetPaths:
    CICIOT2023 = DATA_ROOT / "CICIOT23"
    NF_TON_IOT = DATA_ROOT / "NFTONIoTV2"
    IEC104 = DATA_ROOT / "IEC104"
    # Legacy extracted/coral data path
    CORAL_DATA = PROJECT_ROOT / "ARGUS_Cross_Domain_Results" / "argus_coral_data"

# 3. Artifact Root Resolution
_env_artifact_root = os.getenv("ARGUS_ARTIFACT_ROOT")
if _env_artifact_root:
    ARTIFACT_ROOT = Path(_env_artifact_root).resolve()
else:
    ARTIFACT_ROOT = PROJECT_ROOT / "artifacts"

class ArtifactPaths:
    MODELS = ARTIFACT_ROOT / "models"
    PREDICTIONS = ARTIFACT_ROOT / "predictions"
    METRICS = ARTIFACT_ROOT / "metrics"
    FIGURES = ARTIFACT_ROOT / "figures"
    REPORTS = ARTIFACT_ROOT / "reports"
    LOGS = ARTIFACT_ROOT / "logs"

    @classmethod
    def create_all(cls):
        for path in [cls.MODELS, cls.PREDICTIONS, cls.METRICS, cls.FIGURES, cls.REPORTS, cls.LOGS]:
            path.mkdir(parents=True, exist_ok=True)

# Create artifact directories lazily if accessed (or let scripts create them)
