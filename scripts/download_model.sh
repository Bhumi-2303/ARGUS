#!/usr/bin/env bash
# download_model.sh — Download ARGUS trained model from artifact storage.
#
# Usage:
#   ./scripts/download_model.sh [target_dir]
#
# Environment variables:
#   MODEL_ARTIFACT_URL  - URL to download the model from (GCS, S3, or HTTP)
#   MODEL_PATH          - Local path to save the model (default: models/model_d2_coral.txt)

set -euo pipefail

TARGET_DIR="${1:-models}"
MODEL_FILE="${TARGET_DIR}/model_d2_coral.txt"
ARTIFACT_URL="${MODEL_ARTIFACT_URL:-}"

mkdir -p "${TARGET_DIR}"

if [ -f "${MODEL_FILE}" ]; then
    echo "[✓] Model already exists at ${MODEL_FILE}. Skipping download."
    exit 0
fi

# If local phase3_results model exists (dev mode), copy it
LOCAL_MODEL="phase3_results/models/model_d2_coral.txt"
if [ -f "${LOCAL_MODEL}" ]; then
    echo "[*] Copying model from local phase3_results..."
    cp "${LOCAL_MODEL}" "${MODEL_FILE}"
    echo "[✓] Model copied to ${MODEL_FILE}"
    exit 0
fi

# Download from artifact storage
if [ -z "${ARTIFACT_URL}" ]; then
    echo "[!] ERROR: MODEL_ARTIFACT_URL is not set and no local model found."
    echo "    Set MODEL_ARTIFACT_URL to the GCS/S3/HTTP URL of the trained model."
    echo "    Example: export MODEL_ARTIFACT_URL=gs://argus-models/model_d2_coral.txt"
    exit 1
fi

echo "[*] Downloading model from ${ARTIFACT_URL}..."

# Support GCS, S3, and HTTP URLs
case "${ARTIFACT_URL}" in
    gs://*)
        gsutil cp "${ARTIFACT_URL}" "${MODEL_FILE}"
        ;;
    s3://*)
        aws s3 cp "${ARTIFACT_URL}" "${MODEL_FILE}"
        ;;
    http://*|https://*)
        curl -fSL -o "${MODEL_FILE}" "${ARTIFACT_URL}"
        ;;
    *)
        echo "[!] Unsupported URL scheme: ${ARTIFACT_URL}"
        exit 1
        ;;
esac

echo "[✓] Model downloaded to ${MODEL_FILE}"
