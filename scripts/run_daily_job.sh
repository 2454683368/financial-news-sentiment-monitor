#!/bin/zsh
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE_DIR"

mkdir -p logs
LOG_FILE="logs/daily_job_$(date +%F).log"

echo "[$(date '+%F %T')] Starting daily job" | tee -a "$LOG_FILE"
source .venv/bin/activate
python scripts/run_daily.py --publish 2>&1 | tee -a "$LOG_FILE"
echo "[$(date '+%F %T')] Daily job finished" | tee -a "$LOG_FILE"
