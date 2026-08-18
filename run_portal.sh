#!/usr/bin/env bash
# ==============================================================================
# Dispatch Presentation Layer - One-Command Startup Script
# Level 1 Transport (L1truck.com)
# ==============================================================================

set -e

PORT=${PORT:-5000}
HOST=${HOST:-"0.0.0.0"}

echo "============================================================"
echo " Starting Dispatch Presentation Layer Portal Server..."
echo " Domain Target: L1truck.com"
echo " Target Host: ${HOST}:${PORT}"
echo "============================================================"

# 1. Kill any existing process on port
echo "[1/4] Checking for conflicting processes on port ${PORT}..."
kill $(lsof -t -i:${PORT}) 2>/dev/null || true

# 2. Install dependencies
echo "[2/4] Verifying dependencies..."
python3 -m pip install -q flask pytest gunicorn

# 3. Launch application server in background
echo "[3/4] Launching Dispatch Flask application server..."
PYTHONPATH=. python3 app.py > flask_app.log 2>&1 &
SERVER_PID=$!

echo "Server running under PID ${SERVER_PID}."
echo "Waiting 3 seconds for server boot..."
sleep 3

# 4. Verify endpoints
echo "[4/4] Verifying local health..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:${PORT}/)

if [ "$HTTP_CODE" -eq 200 ]; then
  echo "============================================================"
  echo " SUCCESS: Dispatch Presentation Layer is LIVE!"
  echo " Access Points:"
  echo " - Public Home:          http://${HOST}:${PORT}/"
  echo " - Driver Cockpit:        http://${HOST}:${PORT}/driver"
  echo " - Operations Portal:     http://${HOST}:${PORT}/operations"
  echo " - Stakeholder Window:    http://${HOST}:${PORT}/stakeholder"
  echo " - Legacy L2-COS Redirect: http://${HOST}:${PORT}/l2-cos"
  echo "============================================================"
else
  echo "ERROR: Server health check returned HTTP ${HTTP_CODE}."
  cat flask_app.log
  exit 1
fi
