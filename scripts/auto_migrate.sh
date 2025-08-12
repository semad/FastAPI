#!/bin/bash

# Auto Migration Script for FastAPI
# This script automatically runs database migrations and creates tables

echo "🚀 Auto Migration Script"
echo "📊 Running database setup..."

# Change to project root
cd "$(dirname "$0")/.."

# Run the Python migration script
python scripts/auto_migrate.py

if [ $? -eq 0 ]; then
    echo "✅ Migration completed successfully!"
else
    echo "❌ Migration failed!"
    exit 1
fi
