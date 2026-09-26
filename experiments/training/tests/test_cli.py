import pytest
import subprocess
import sys
from pathlib import Path

def test_train_cli_help():
    result = subprocess.run([sys.executable, "training/train.py", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "ARGUS ML Training Framework" in result.stdout

def test_train_cli_dry_run_random_forest():
    result = subprocess.run([sys.executable, "training/train.py", "--model", "random_forest", "--dry-run"], capture_output=True, text=True)
    assert result.returncode == 0
    
def test_train_cli_dry_run_all():
    result = subprocess.run([sys.executable, "training/train.py", "--all", "--dry-run"], capture_output=True, text=True)
    assert result.returncode == 0
    
def test_train_cli_invalid_model():
    result = subprocess.run([sys.executable, "training/train.py", "--model", "invalid", "--dry-run"], capture_output=True, text=True)
    assert result.returncode != 0
