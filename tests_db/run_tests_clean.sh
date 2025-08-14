#!/bin/bash

# Enhanced Test Runner with Database Cleanup
# This script runs tests with automatic database cleanup

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 FastAPI Enhanced Test Runner with Database Cleanup"
echo "====================================================="
echo "Project: $PROJECT_ROOT"
echo "Script: $SCRIPT_DIR/run_tests_with_cleanup.py"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "$SCRIPT_DIR/run_tests_with_cleanup.py" ]]; then
    echo "❌ Enhanced test runner script not found at $SCRIPT_DIR/run_tests_with_cleanup.py"
    exit 1
fi

# Check if cleanup script exists
if [[ ! -f "$SCRIPT_DIR/cleanup_db.py" ]]; then
    echo "❌ Database cleanup script not found at $SCRIPT_DIR/cleanup_db.py"
    exit 1
fi

echo "🚀 Starting enhanced test runner..."
echo

# Run the enhanced test runner with all arguments passed through
cd "$PROJECT_ROOT"
python3 "$SCRIPT_DIR/run_tests_with_cleanup.py" "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo
    echo "✅ Test execution completed successfully!"
else
    echo
    echo "❌ Test execution completed with errors (exit code: $exit_code)"
fi

exit $exit_code
