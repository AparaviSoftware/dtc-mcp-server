#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PACKAGE_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PACKAGE_ROOT/.venv"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python3
if ! command_exists python3; then
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH" || {
        exit 1
    }
fi

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
elif [ -f "$VENV_PATH/Scripts/activate" ]; then
    source "$VENV_PATH/Scripts/activate"
else
    exit 1
fi

# Install requirements
pip install -r "$PACKAGE_ROOT/requirements.txt" 1>&2 || {
    exit 1
}
