import sys
from pathlib import Path
try:
    from src.argus.core.config.paths import PROJECT_ROOT, DATA_ROOT, ArtifactPaths
    print("Import from project root successful")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
except Exception as e:
    print(f"Import failed: {e}")
