#!/bin/bash
# Exit immediately if any command fails
set -e

# --- 1. Navigate to the project root (up two levels from system/core) ---
# Tự động xác định và chuyển đến thư mục gốc
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_ROOT"

echo "ROOT: $(pwd)"


# --- 2. Check and create Venv ---
VENV_NAME=".venv"
VENV_PYTHON="$VENV_NAME/bin/python"

if [ -d "$VENV_NAME" ]; then
    echo "VENV: Already exists."
else
    echo "VENV: Creating..."
    # Sử dụng python3 và kiểm tra lỗi
    python3 -m venv "$VENV_NAME"
    
    if [ $? -ne 0 ]; then
        echo "ERROR: VENV creation failed. Check python3 PATH."
        exit 1
    else
        echo "VENV: Created successfully."
    fi
fi


# --- 3. Update PIP (Always run if Venv exists) ---
if [ -f "$VENV_PYTHON" ]; then
    echo "PIP: Updating..."
    
    # Execute the VENV's python to upgrade pip
    "$VENV_PYTHON" -m pip install --upgrade pip
    
    if [ $? -ne 0 ]; then
        echo "WARNING: PIP update failed. Proceeding."
    else
        echo "PIP: Updated."
    fi
fi


echo "SETUP: Process finished."