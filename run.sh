#!/bin/bash
# Mindanawa Disaster Informatics Lab (MDIL) - Iligan Flood Simulation
# Standalone macOS/Linux Click-to-Run Script

# Move to the directory containing this script
CDPATH="" cd -- "$(dirname -- "$0")"

echo "======================================================================"
echo "    ILIGAN CITY FLOOD EVACUATION & SITUATION AWARENESS SIMULATOR      "
echo "======================================================================"
echo "[*] Checking Python environment dependencies..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[-] Error: python3 is not installed or not in system PATH."
    echo "[-] Please install Python 3.9+ and try again."
    read -p "Press [Enter] to exit..."
    exit 1
fi

echo "[*] Launching click-to-run system..."
python3 run.py
