import kaggle
import os
import sys

dataset_name = sys.argv[1]
output_path = sys.argv[2]

print(f"Downloading {dataset_name} to {output_path}...")
kaggle.api.authenticate()
kaggle.api.dataset_download_files(dataset_name, path=output_path, unzip=True)
print(f"Downloaded {dataset_name} successfully.")
