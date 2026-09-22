#!/bin/bash
set -e

echo "Starting Clean-Clone Test..."

export TMPDIR="$PWD/scratch_tmp"
export PIP_CACHE_DIR="$PWD/scratch_pip_cache"
mkdir -p "$TMPDIR" "$PIP_CACHE_DIR"

# 1. Fresh clone from git
CLONE_DIR="$PWD/scratch_argus_clone"
rm -rf $CLONE_DIR
echo "Cloning from local git repository..."
git clone file://$(pwd) $CLONE_DIR
cd $CLONE_DIR

# 2. New venv and native project install
echo "Creating new venv and installing project natively..."
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[test]

# 3. Restore artifacts from backup
echo "Attempting to restore artifacts from Day 1 backup..."
make restore-artifacts

if [ ! -f "artifacts/models/xgb_source.json" ]; then
    echo "FAILED: Artifacts missing after restore!"
    exit 1
fi

# 4. Run pytest
echo "Running pytest..."
pytest tests/e2e/test_day3.py

# 5. Start API
echo "Starting API..."
uvicorn argus.api.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!
sleep 5

# 6. Run smoke request
echo "Running smoke request..."
curl -X POST http://127.0.0.1:8000/analyze \
    -H "Content-Type: application/json" \
    -d '{"flows": [{"pkt_mean_to_max": 0.5, "tcp_flag_density": 1, "log_pkt_mean": 2.1, "log_pkt_max": 3.4}]}'

curl -X GET http://127.0.0.1:8000/health

# 7. Launch dashboard headless
echo "Launching dashboard headless..."
streamlit run frontend/app.py --server.headless true &
STREAMLIT_PID=$!
sleep 3

# Cleanup
echo "Cleaning up..."
kill $API_PID
kill $STREAMLIT_PID

echo "Clean-Clone Test Passed!"
