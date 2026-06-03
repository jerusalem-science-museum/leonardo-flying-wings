#!/bin/bash

# ==============================================================================
# Jerusalem Science Museum - Energy & Air Pressure Exhibit Launch Script
# Compliant with JSM Kiosk App Setup (.venv standard)
# ==============================================================================

# Ensure the script runs from the directory it is located in
cd "$(dirname "$0")"

echo "=================================================="
echo " Starting JSM Exhibit: leonardo-flying-wings"
echo "=================================================="

# 1. Display & Screen Configuration (Museum Floor Standards)
export DISPLAY=:0
xset s off      # Disable screen saver timeout
xset -dpms      # Disable Display Power Management Signaling
xset s noblank  # Prevent screen from short-term blanking

# 2. Python Virtual Environment (.venv) Activation
# Standard JSM Kiosk configuration uses hidden .venv
if [ -d ".venv" ]; then
    echo "[INFO] Activating virtual environment (.venv)..."
    source .venv/Scripts/activate
else
    echo "[WARNING] '.venv' directory not found. Proceeding with system Python."
fi

# 3. Permanent Execution & Crash Recovery Loop
while true; do
    echo "[LAUNCH] Launching main.py..."
    python3 main.py
    
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[EXIT] Application closed normally by user. Terminating script."
        break
    else
        echo "[CRASH] Application exited unexpectedly (Code: $EXIT_CODE)."
        echo "[RECOVERY] Restarting exhibit loop in 3 seconds..."
        sleep 3
    fi
done