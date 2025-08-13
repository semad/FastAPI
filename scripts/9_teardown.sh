#!/bin/bash

# Enhanced Teardown Script for FastAPI
# This script stops all services and cleans up

echo "🛑 Enhanced Teardown Script"
echo "==========================="

# Stop all services
echo "🐳 Stopping Docker services..."
docker-compose down

# Remove containers and networks
echo "🧹 Cleaning up containers and networks..."
docker-compose down --remove-orphans

# Optionally remove volumes (uncomment if you want to reset data)
echo "🗑️  Removing volumes..."
docker-compose down -v

echo ""
echo "✅ Teardown completed!"
