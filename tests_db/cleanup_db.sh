#!/bin/bash

# Database Cleanup Script for Testing
# This script cleans up the test database before running tests

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🧹 FastAPI Test Database Cleanup"
echo "================================="
echo "Project: $PROJECT_ROOT"
echo "Script: $SCRIPT_DIR/cleanup_db.py"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "$SCRIPT_DIR/cleanup_db.py" ]]; then
    echo "❌ Cleanup script not found at $SCRIPT_DIR/cleanup_db.py"
    exit 1
fi

# Check if Docker is running (assuming PostgreSQL is in Docker)
if ! docker info &> /dev/null; then
    echo "⚠️  Docker is not running. Make sure your PostgreSQL database is accessible."
    echo "   If using a local PostgreSQL instance, the cleanup script will attempt to connect directly."
fi

echo "🚀 Starting database cleanup..."
echo

# Run the cleanup script
cd "$PROJECT_ROOT"
python3 "$SCRIPT_DIR/cleanup_db.py"

if [ $? -eq 0 ]; then
    echo
    echo "✅ Database cleanup completed successfully!"
    echo "🚀 You can now run your tests with a clean database."
else
    echo
    echo "❌ Database cleanup failed!"
    echo "💡 Check the error messages above and ensure your database is accessible."
    exit 1
fi
