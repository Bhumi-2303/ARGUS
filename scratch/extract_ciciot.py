import glob
import os
import zipfile

zip_files = glob.glob('data/cic_iot_2023/processed/*.csv.zip')
for zf in zip_files:
    try:
        with zipfile.ZipFile(zf, 'r') as zip_ref:
            zip_ref.extractall('data/cic_iot_2023/processed/')
        os.remove(zf)
        print(f"Extracted and removed {zf}")
    except Exception as e:
        print(f"Failed to extract {zf}: {e}")
