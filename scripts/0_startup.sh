#!/bin/bash

# Enhanced Startup Script for FastAPI
# This script starts all services and ensures they're healthy

echo "🚀 Enhanced Startup Script"
echo "=========================="

# Start all services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run health check
echo "🏥 Running health check..."
./scripts/1_inital_health_checkup.sh

# Run database setup if needed
#echo "📊 Setting up database..."
#./scripts/auto_migrate.sh

# Create superuser if needed
#echo "👤 Creating superuser..."
#docker exec fastapi-web-1 python -m src.scripts.create_first_superuser

echo ""
echo "✅ Startup completed!"
echo "🌐 FastAPI available at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
