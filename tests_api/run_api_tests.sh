#!/bin/bash

# API Test Runner Script for FastAPI Application
# This script runs API tests for the FastAPI application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Run the Python test runner with all arguments passed through
python "$SCRIPT_DIR/run_api_tests.py" "$@"
