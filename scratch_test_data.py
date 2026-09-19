import sys
from pathlib import Path
from src.argus.core.config.paths import DatasetPaths

def check_data(name, path):
    print(f"{name}: {'AVAILABLE' if path.exists() else 'NOT AVAILABLE'} ({path})")

check_data("CICIoT2023", DatasetPaths.CICIOT2023)
check_data("NF-ToN-IoT", DatasetPaths.NF_TON_IOT)
check_data("IEC104", DatasetPaths.IEC104)
