#!/bin/bash
# High-End Lab Terminal Ignition Script

# Navigate to the terminal directory
cd "$(dirname "$0")"

# Activate the virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "ERROR: Virtual environment not found. Run setup first."
    exit 1
fi

# Set default port if not provided
PORT=${1:-8081}

echo "========================================"
echo "  HUMAN PATTERN LAB: CODA INTERFACE"
echo "  STATUS: IGNITING THERMAL CORE..."
echo "  URL: http://localhost:$PORT"
echo "========================================"

# Run the server
python3 server.py
