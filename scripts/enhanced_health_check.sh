#!/bin/bash

# Enhanced Health Check Script for FastAPI
# This script checks the health of all services

echo "🏥 Enhanced Health Check Script"
echo "================================"

# Check Docker containers
echo "🐳 Checking Docker containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🔍 Checking service endpoints..."

# Check FastAPI health
echo "📡 FastAPI Health Check:"
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ FastAPI is running"
else
    echo "   ❌ FastAPI is not responding"
fi

# Check PostgreSQL
echo "🐘 PostgreSQL Health Check:"
if docker exec fastapi-db-1 pg_isready -U postgres > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL is running"
else
    echo "   ❌ PostgreSQL is not responding"
fi

# Check Redis
echo "🔴 Redis Health Check:"
if docker exec fastapi-redis-1 redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis is running"
else
    echo "   ❌ Redis is not responding"
fi

echo ""
echo "✅ Health check completed!"
