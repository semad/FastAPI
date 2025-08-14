#!/bin/bash

# Health Check Script Wrapper for FastAPI Application
# This script runs the health check to verify the service is running and healthy

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Run the Python health check script with all arguments passed through
python "$SCRIPT_DIR/health_check.py" "$@"
