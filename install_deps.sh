#!/bin/bash
# Silent dependency installation script
cd "$(dirname "$0")"
python3 -m venv .venv 2>/dev/null
.venv/bin/pip install --quiet --upgrade pip setuptools wheel 2>/dev/null
.venv/bin/pip install --quiet -r requirements.txt 2>/dev/null
echo "Installation complete. Check with: .venv/bin/pip list"

