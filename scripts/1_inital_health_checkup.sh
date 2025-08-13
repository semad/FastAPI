#!/bin/bash

# First Checkup Script for FastAPI Application
# This script checks all Docker containers, reads their logs, and verifies the application is working.
#set -x
set -uo pipefail

# Function to handle errors gracefully
handle_error() {
    local exit_code=$?
    print_status "$RED" "❌ Script encountered an error (exit code: $exit_code)"
    print_status "$YELLOW" "Continuing with remaining checks..."
    return 0
}

# Set error handling for critical errors only
trap handle_error ERR

# Enhanced colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Global variables
declare -a CONTAINERS
declare -a ISSUES
SUCCESS_COUNT=0
TOTAL_CHECKS=0

# Function to print colored output with enhanced formatting
print_status() {
    local color=$1
    local message="$2"
    echo -e "${color}${message}${NC}"
}

# Function to print a beautiful header
print_header() {
    local title="$1"
    local color="$2"
    echo -e "\n${color}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    printf "║ %-70s ║\n" "$title"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to print a section header
print_section() {
    local title="$1"
    local color="$2"
    echo -e "\n${color}${BOLD}▶️  $title${NC}"
    echo -e "${color}────────────────────────────────────────────────────────────────────────${NC}"
}

# Function to print a progress bar
print_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))
    
    printf "\r${CYAN}["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] ${BOLD}%d%%${NC}" "$percentage"
    
    if [[ $current -eq $total ]]; then
        echo ""
    fi
}

# Function to print a container status box
print_container_box() {
    local name="$1"
    local service="$2"
    local state="$3"
    local status="$4"
    
    local state_color
    local state_icon
    case "$state" in
        "running")
            state_color="$GREEN"
            state_icon="🟢"
            ;;
        "exited")
            state_color="$RED"
            state_icon="🔴"
            ;;
        "created")
            state_color="$YELLOW"
            state_icon="🟡"
            ;;
        *)
            state_color="$PURPLE"
            state_icon="⚪"
            ;;
    esac
    
    echo -e "\n${CYAN}┌─ Container: ${BOLD}$name${NC}"
    echo -e "${CYAN}├─ Service:   $service"
    echo -e "${CYAN}├─ State:     ${state_color}${state_icon} $state${NC}"
    echo -e "${CYAN}└─ Status:    $status${NC}"
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
    print_section "Container Status Check" "$BLUE"
    
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
        
        # Only add containers that have valid names (not headers) and exclude one-time setup containers
        if [[ -n "$name" && "$name" != "Name" && "$name" != "NAME" && ! "$name" =~ ^[[:space:]]*$ ]]; then
            # Filter out one-time setup containers that are not part of regular health checks
            if [[ ! "$name" =~ create_superuser ]] && [[ ! "$name" =~ create_tier ]]; then
                CONTAINERS+=("$name|$state|$status|$service")
            fi
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
    
    # Check if container exists and get its state
    if ! docker ps -a --format "{{.Names}}" | grep -q "^${container_name}$"; then
        echo "Container not found"
        return 1
    fi
    
    # Get container state
    local container_state
    container_state=$(docker ps -a --format "{{.Names}}\t{{.Status}}" | grep "^${container_name}\t" | cut -f2)
    
    # If container is not running, try to get logs from when it was last running
    if [[ ! "$container_state" =~ Up ]]; then
        echo "Container is not running (Status: $container_state)"
        echo "Attempting to retrieve last available logs..."
    fi
    
    # Use a simple approach to get logs without hanging
    # Try to get logs, but limit output to prevent hanging
    local logs
    logs=$(docker logs "$container_name" --tail "$lines" 2>&1 | head -100 2>/dev/null || echo "Failed to get logs or container not accessible")
    
    # If logs are empty or failed, provide more context
    if [[ -z "$logs" || "$logs" == "Failed to get logs or container not accessible" ]]; then
        echo "No logs available for container $container_name"
        echo "Container state: $container_state"
    else
        echo "$logs"
    fi
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
    
    # Skip analysis if logs indicate container issues
    if [[ "$logs" =~ "Container not found" ]] || [[ "$logs" =~ "No logs available" ]]; then
        print_status "$YELLOW" "   ⚠️  Container logs not accessible"
        ISSUES+=("$container_name: Logs not accessible")
        return 0
    fi
    
    # Check for common error patterns
    if echo "$logs" | grep -qi "ERROR\|Exception\|Traceback\|Failed"; then
        print_status "$YELLOW" "   ⚠️  Found potential issues in logs:"
        error_found=true
        # Show only the first few error lines with better formatting
        echo "$logs" | grep -i "ERROR\|Exception\|Traceback\|Failed" | head -3 | sed 's/^/      🔴 /'
    fi
    
    if [[ "$error_found" == true ]]; then
        ISSUES+=("$container_name: Log errors detected")
        return 0
    else
        print_status "$GREEN" "   ✅ No errors found in logs"
        return 0
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
    print_header "🏥 COMPREHENSIVE HEALTH CHECKS" "$PURPLE"
    
    print_status "$BLUE" "Processing ${#CONTAINERS[@]} containers..."
    
    local current=0
    for container_info in "${CONTAINERS[@]}"; do
        ((current++))
        echo "current: $current"
        print_progress "$current" "${#CONTAINERS[@]}"
        
        IFS='|' read -r container_name state status service <<< "$container_info"
        
        print_container_box "$container_name" "$service" "$state" "$status"
        
        # Get logs for ALL containers regardless of state
        local logs
        logs=$(get_container_logs "$container_name")
        
        # Analyze logs for errors
        analyze_logs_for_errors "$container_name" "$logs"
        
        # Check if container is running
        if [[ "$state" == "running" ]]; then
            print_status "$GREEN" "   ✅ Container is running"
            
            # Run service-specific checks
            if check_specific_service "$service" "$container_name"; then
                ((SUCCESS_COUNT++))
            fi
            ((TOTAL_CHECKS++))
            
        else
            print_status "$RED" "   ❌ Container is not running (State: $state)"
            ISSUES+=("Container $container_name is not running")
            ((TOTAL_CHECKS++))
        fi
    done
    
    print_progress "${#CONTAINERS[@]}" "${#CONTAINERS[@]}"
}

# Function to generate report
generate_report() {
    print_header "📊 HEALTH CHECK REPORT" "$CYAN"
    
    echo -e "\n${BOLD}📈 Overall Status:${NC}"
    echo -e "   ${CYAN}Successful checks:${NC} ${BOLD}$SUCCESS_COUNT/$TOTAL_CHECKS${NC}"
    echo -e "   ${CYAN}Issues found:${NC} ${BOLD}${#ISSUES[@]}${NC}"
    
    if [[ ${#ISSUES[@]} -gt 0 ]]; then
        echo -e "\n${BOLD}⚠️  Issues Summary:${NC}"
        for i in "${!ISSUES[@]}"; do
            echo -e "   ${RED}$((i+1)). ${ISSUES[$i]}${NC}"
        done
    fi
    
    echo -e "\n${BOLD}🔍 Container Status:${NC}"
    for container_info in "${CONTAINERS[@]}"; do
        IFS='|' read -r container_name state status service <<< "$container_info"
        local status_icon
        local status_color
        if [[ "$state" == "running" ]]; then
            status_icon="✅"
            status_color="$GREEN"
        else
            status_icon="❌"
            status_color="$RED"
        fi
        echo -e "   $status_icon ${BOLD}$container_name${NC}: ${status_color}$state${NC} ($status)"
    done
    
    echo -e "\n${BOLD}🌐 Service Endpoints:${NC}"
    echo -e "   ${CYAN}• FastAPI App:${NC} http://localhost:8000"
    echo -e "   ${CYAN}• API Docs:${NC} http://localhost:8000/docs"
    echo -e "   ${CYAN}• Admin Panel:${NC} http://localhost:8000/admin"
    echo -e "   ${CYAN}• PGAdmin:${NC} http://localhost:5050"
    echo -e "   ${CYAN}• Redis Insight:${NC} http://localhost:5540"
    
    if [[ $SUCCESS_COUNT -eq $TOTAL_CHECKS && ${#ISSUES[@]} -eq 0 ]]; then
        echo -e "\n${GREEN}${BOLD}🎉 All systems are running successfully!${NC}"
    else
        echo -e "\n${YELLOW}${BOLD}⚠️  Some issues were detected. Please review the logs above.${NC}"
    fi
}

# Function to check dependencies
check_dependencies() {
    print_section "Dependency Check" "$BLUE"
    
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
    print_header "🚀 FastAPI Application Health Checkup" "$BLUE"
    
    # Check dependencies
    check_dependencies
    
    # Get container status
    if ! get_container_status; then
        exit 1
    fi
    
    # Run health checks
    print_status "$BLUE" "Starting health checks..."
    run_health_checks
    print_status "$BLUE" "Health checks completed."
    
    # Generate report
    print_status "$BLUE" "Generating report..."
    generate_report
    print_status "$BLUE" "Report generation completed."
}

# Trap to handle script interruption
trap 'echo -e "\n\n⏹️  Checkup interrupted by user"; exit 1' INT

# Run main function
main "$@"
