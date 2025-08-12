#!/bin/bash

# Simple First Checkup Script for FastAPI Application
# This script checks all Docker containers and verifies the application is working.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if a service is responding
check_service() {
    local name=$1
    local url=$2
    local description=$3
    
    print_status "$BLUE" "🌐 Checking $description ($name)..."
    
    if curl -s -f "$url" >/dev/null 2>&1; then
        print_status "$GREEN" "✅ $description is responding"
        return 0
    else
        print_status "$RED" "❌ $description is not responding"
        return 1
    fi
}

# Function to check container logs for errors
check_container_logs() {
    local container_name=$1
    local service_name=$2
    
    print_status "$BLUE" "📋 Checking $service_name ($container_name)..."
    
    # Get the last 20 lines of logs
    local logs
    logs=$(docker logs "$container_name" --tail 20 2>&1 || echo "Failed to get logs")
    
    # Check for common error patterns
    if echo "$logs" | grep -qi "ERROR\|Exception\|Traceback\|Failed\|Connection refused"; then
        print_status "$YELLOW" "   ⚠️  Found potential issues in logs:"
        echo "$logs" | grep -i "ERROR\|Exception\|Traceback\|Failed\|Connection refused" | head -3 | sed 's/^/      - /'
    else
        print_status "$GREEN" "   ✅ No errors found in logs"
    fi
}

# Main execution
main() {
    print_status "$BLUE" "🚀 FastAPI Application Simple Checkup"
    echo "============================================================"
    
    # Check if docker-compose is running
    if ! docker-compose ps >/dev/null 2>&1; then
        print_status "$RED" "❌ Docker Compose is not running. Start it first with 'docker-compose up -d'"
        exit 1
    fi
    
    print_status "$GREEN" "✅ Docker Compose is running"
    
    # Show container status
    print_status "$BLUE" "\n📊 Container Status:"
    docker-compose ps
    
    # Check each service
    print_status "$BLUE" "\n🏥 Running Health Checks..."
    echo "============================================================"
    
    # Check web service
    check_service "FastAPI Web" "http://localhost:8000/docs" "FastAPI Web Service"
    
    # Check database
    print_status "$BLUE" "🗄️  Checking database connection..."
    if docker exec fastapi-db-1 pg_isready -U postgres >/dev/null 2>&1; then
        print_status "$GREEN" "✅ Database is accepting connections"
    else
        print_status "$RED" "❌ Database connection failed"
    fi
    
    # Check Redis
    print_status "$BLUE" "🔴 Checking Redis connection..."
    if docker exec fastapi-redis-1 redis-cli ping 2>/dev/null | grep -q "PONG"; then
        print_status "$GREEN" "✅ Redis is responding (PONG)"
    else
        print_status "$RED" "❌ Redis connection failed"
    fi
    
    # Check container logs
    print_status "$BLUE" "\n📋 Checking Container Logs..."
    echo "============================================================"
    
    check_container_logs "fastapi-web-1" "Web Service"
    check_container_logs "fastapi-db-1" "Database"
    check_container_logs "fastapi-redis-1" "Redis"
    check_container_logs "fastapi-worker-1" "Worker"
    
    # Summary
    print_status "$BLUE" "\n📊 Summary"
    echo "============================================================"
    echo "🌐 Service Endpoints:"
    echo "   - FastAPI App: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - Admin Panel: http://localhost:8000/admin"
    echo "   - PGAdmin: http://localhost:5050"
    echo "   - Redis Insight: http://localhost:5540"
    
    print_status "$GREEN" "\n🎉 Checkup completed! Check the results above."
}

# Run main function
main "$@"
