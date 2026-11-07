#!/bin/bash
set -e

echo "Starting HAI download..."
kaggle datasets download -d icsdataset/hai-security-dataset -p scratch/hai_tmp --unzip &
HAI_PID=$!

echo "Starting CICIoT2023 download..."
kaggle datasets download -d madhavmalhotra/unb-cic-iot-dataset -p scratch/cic_tmp --unzip &
CIC_PID=$!

echo "Starting TON_IoT download..."
kaggle datasets download -d mohammedaddoun/ton-iot -p scratch/ton_tmp --unzip &
TON_PID=$!

echo "Waiting for downloads to finish..."
wait $HAI_PID
echo "HAI downloaded."

wait $CIC_PID
echo "CICIoT2023 downloaded."

wait $TON_PID
echo "TON_IoT downloaded."

echo "All downloads finished."

# Move HAI files
mkdir -p data/hai/processed
mv scratch/hai_tmp/hai-22.04/*.csv data/hai/processed/ || true

# Move CICIoT2023 files
mkdir -p data/cic_iot_2023/processed
mv scratch/cic_tmp/wataiData/csv/CICIoT2023/*.csv data/cic_iot_2023/processed/ || true

# Move TON_IoT files
mkdir -p data/ton_iot/network_timestamped
mv scratch/ton_tmp/*.csv data/ton_iot/network_timestamped/ || true

echo "Files moved successfully."
