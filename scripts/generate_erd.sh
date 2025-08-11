#!/bin/bash

# ERD Generation Script Wrapper
# This script makes it easier to generate ERDs for the FastAPI application

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Check if Python script exists
if [ ! -f "scripts/generate_erd.py" ]; then
    echo "Error: generate_erd.py not found in scripts directory"
    exit 1
fi

# Run the ERD generator with all arguments passed through
python scripts/generate_erd.py "$@"
