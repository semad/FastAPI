#!/bin/bash

# First Checkup Script for FastAPI Application
# This script checks all Docker containers, reads their logs, and verifies the application is working.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables
declare -a CONTAINERS
declare -a ISSUES
SUCCESS_COUNT=0
TOTAL_CHECKS=0

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to run a command and return success status
run_command() {
    local command="$1"
    local output
    local exit_code
    
    if output=$(eval "$command" 2>&1); then
        exit_code=0
    else
        exit_code=$?
    fi
    
    echo "$output"
    return $exit_code
}

# Function to get container status
get_container_status() {
    print_status "$BLUE" "🔍 Checking container status..."
    
    if ! docker-compose ps >/dev/null 2>&1; then
        print_status "$RED" "❌ Failed to get container status. Make sure docker-compose is running."
        return 1
    fi
    
    # Parse container information using a simpler approach
    while IFS= read -r line; do
        # Skip header lines and empty lines
        if [[ "$line" =~ ^[[:space:]]*$ ]] || [[ "$line" =~ ^Name[[:space:]]+Command ]] || [[ "$line" =~ ^NAME[[:space:]]+IMAGE ]]; then
            continue
        fi
        
        # Parse the docker-compose ps output
        local name=$(echo "$line" | awk '{print $1}')
        local service=$(echo "$line" | awk '{print $2}')
        local status=$(echo "$line" | awk '{for(i=3;i<=NF;i++) printf "%s ", $i; print ""}' | sed 's/ $//')
        
        # Determine state based on status
        local state="unknown"
        if [[ "$status" =~ Up ]]; then
            state="running"
        elif [[ "$status" =~ Exit ]]; then
            state="exited"
        elif [[ "$status" =~ Created ]]; then
            state="created"
        fi
        
        # Only add containers that have valid names (not headers)
        if [[ -n "$name" && "$name" != "Name" && "$name" != "NAME" && ! "$name" =~ ^[[:space:]]*$ ]]; then
            CONTAINERS+=("$name|$state|$status|$service")
        fi
    done < <(docker-compose ps)
    
    if [[ ${#CONTAINERS[@]} -eq 0 ]]; then
        print_status "$RED" "❌ No containers found."
        return 1
    fi
    
    print_status "$GREEN" "✅ Found ${#CONTAINERS[@]} containers"
}

# Function to get container logs
get_container_logs() {
    local container_name="$1"
    local lines="${2:-50}"
    
    docker logs "$container_name" --tail "$lines" 2>&1 || echo "Failed to get logs"
}

# Function to check web service
check_web_service() {
    local container_name="$1"
    print_status "$BLUE" "🌐 Checking web service ($container_name)..."
    
    # Wait a bit for the service to start
    sleep 2
    
    # Try to connect to the web service
    local http_code
    http_code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/docs 2>/dev/null || echo "000")
    
    if [[ "$http_code" == "200" ]]; then
        print_status "$GREEN" "✅ Web service is responding (HTTP 200)"
        return 0
    else
        print_status "$RED" "❌ Web service check failed (HTTP $http_code)"
        return 1
    fi
}

# Function to check database connection
check_database_connection() {
    local container_name="$1"
    print_status "$BLUE" "🗄️  Checking database connection ($container_name)..."
    
    # Check if PostgreSQL is accepting connections
    if docker exec fastapi-db-1 pg_isready -U postgres >/dev/null 2>&1; then
        print_status "$GREEN" "✅ Database is accepting connections"
        return 0
    else
        print_status "$RED" "❌ Database connection failed"
        return 1
    fi
}

# Function to check Redis connection
check_redis_connection() {
    local container_name="$1"
    print_status "$BLUE" "🔴 Checking Redis connection ($container_name)..."
    
    # Check if Redis is responding to ping
    local redis_response
    redis_response=$(docker exec fastapi-redis-1 redis-cli ping 2>/dev/null || echo "FAILED")
    
    if [[ "$redis_response" == "PONG" ]]; then
        print_status "$GREEN" "✅ Redis is responding (PONG)"
        return 0
    else
        print_status "$RED" "❌ Redis connection failed: $redis_response"
        return 1
    fi
}

# Function to analyze logs for errors
analyze_logs_for_errors() {
    local container_name="$1"
    local logs="$2"
    local error_found=false
    
    # Common error patterns
    local error_patterns=(
        "ERROR"
        "Exception"
        "Traceback"
        "Failed"
        "Connection refused"
        "Connection timeout"
        "Database.*error"
        "Redis.*error"
        "Import.*error"
        "ModuleNotFoundError"
        "AttributeError"
        "TypeError"
        "ValueError"
    )
    
    for pattern in "${error_patterns[@]}"; do
        if echo "$logs" | grep -qi "$pattern"; then
            if [[ "$error_found" == false ]]; then
                print_status "$YELLOW" "   ⚠️  Found potential issues in logs:"
                error_found=true
            fi
            echo "$logs" | grep -i "$pattern" | head -3 | sed 's/^/      - /'
        fi
    done
    
    if [[ "$error_found" == true ]]; then
        ISSUES+=("$container_name: Log errors detected")
        return 0
    else
        print_status "$GREEN" "   ✅ No errors found in logs"
        return 1
    fi
}

# Function to check specific service
check_specific_service() {
    local service_name="$1"
    local container_name="$2"
    
    case "$(echo "$service_name" | tr '[:upper:]' '[:lower:]')" in
        *web*)
            check_web_service "$container_name"
            ;;
        *db*|*postgres*)
            check_database_connection "$container_name"
            ;;
        *redis*)
            check_redis_connection "$container_name"
            ;;
        *)
            # For other services, just check if they're running
            return 0
            ;;
    esac
}

# Function to run health checks
run_health_checks() {
    print_status "$BLUE" "\n🏥 RUNNING COMPREHENSIVE HEALTH CHECKS"
    echo "============================================================"
    
    for container_info in "${CONTAINERS[@]}"; do
        IFS='|' read -r container_name state status service <<< "$container_info"
        
        echo -e "\n📋 Container: $container_name"
        echo "   Service: $service"
        echo "   State: $state"
        echo "   Status: $status"
        
        # Check if container is running
        if [[ "$state" == "running" ]]; then
            print_status "$GREEN" "   ✅ Container is running"
            
            # Get logs
            local logs
            logs=$(get_container_logs "$container_name")
            
            # Analyze logs for errors
            analyze_logs_for_errors "$container_name" "$logs"
            
            # Run service-specific checks
            if check_specific_service "$service" "$container_name"; then
                ((SUCCESS_COUNT++))
            fi
            ((TOTAL_CHECKS++))
            
        else
            print_status "$RED" "   ❌ Container is not running (State: $state)"
            ISSUES+=("Container $container_name is not running")
        fi
    done
}

# Function to generate report
generate_report() {
    print_status "$BLUE" "\n📊 HEALTH CHECK REPORT"
    echo "============================================================"
    
    echo -e "\n📈 Overall Status:"
    echo "   Successful checks: $SUCCESS_COUNT/$TOTAL_CHECKS"
    echo "   Issues found: ${#ISSUES[@]}"
    
    if [[ ${#ISSUES[@]} -gt 0 ]]; then
        echo -e "\n⚠️  Issues Summary:"
        for i in "${!ISSUES[@]}"; do
            echo "   $((i+1)). ${ISSUES[$i]}"
        done
    fi
    
    echo -e "\n🔍 Container Status:"
    for container_info in "${CONTAINERS[@]}"; do
        IFS='|' read -r container_name state status service <<< "$container_info"
        local status_icon
        if [[ "$state" == "running" ]]; then
            status_icon="✅"
        else
            status_icon="❌"
        fi
        echo "   $status_icon $container_name: $state ($status)"
    done
    
    echo -e "\n🌐 Service Endpoints:"
    echo "   - FastAPI App: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - Admin Panel: http://localhost:8000/admin"
    echo "   - PGAdmin: http://localhost:5050"
    echo "   - Redis Insight: http://localhost:5540"
    
    if [[ $SUCCESS_COUNT -eq $TOTAL_CHECKS && ${#ISSUES[@]} -eq 0 ]]; then
        print_status "$GREEN" "\n🎉 All systems are running successfully!"
    else
        print_status "$YELLOW" "\n⚠️  Some issues were detected. Please review the logs above."
    fi
}

# Function to check dependencies
check_dependencies() {
    local missing_deps=()
    
    # Check for required commands
    for cmd in docker docker-compose curl jq; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_status "$RED" "❌ Missing required dependencies: ${missing_deps[*]}"
        print_status "$YELLOW" "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_status "$GREEN" "✅ All dependencies are available"
}

# Main execution
main() {
    print_status "$BLUE" "🚀 FastAPI Application First Checkup"
    echo "============================================================"
    
    # Check dependencies
    check_dependencies
    
    # Get container status
    if ! get_container_status; then
        exit 1
    fi
    
    # Run health checks
    run_health_checks
    
    # Generate report
    generate_report
}

# Trap to handle script interruption
trap 'echo -e "\n\n⏹️  Checkup interrupted by user"; exit 1' INT

# Run main function
main "$@"
