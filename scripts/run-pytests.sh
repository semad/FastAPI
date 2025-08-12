#!/bin/bash

# Comprehensive Pytest Runner and Results Archiver
# This script runs all pytest tests, generates detailed reports, and archives results

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$PROJECT_ROOT/test_results"
ARCHIVE_DIR="$RESULTS_DIR/archives"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_NAME="pytest_report_${TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print section header
print_header() {
    local message=$1
    echo -e "\n${CYAN}==========================================${NC}"
    echo -e "${CYAN}  ${message}${NC}"
    echo -e "${CYAN}==========================================${NC}"
}

# Function to check dependencies
check_dependencies() {
    print_header "Checking Dependencies"
    
    local missing_deps=()
    
    # Check for required commands
    for cmd in python pytest git; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_status "$RED" "❌ Missing required dependencies: ${missing_deps[*]}"
        print_status "$YELLOW" "Please install the missing dependencies and try again."
        exit 1
    fi
    
    # Check Python version
    local python_version
    python_version=$(python --version 2>&1 | cut -d' ' -f2)
    print_status "$GREEN" "✅ Python version: $python_version"
    
    # Check pytest version
    local pytest_version
    pytest_version=$(pytest --version 2>&1 | cut -d' ' -f2)
    print_status "$GREEN" "✅ Pytest version: $pytest_version"
    
    print_status "$GREEN" "✅ All dependencies are available"
}

# Function to setup directories
setup_directories() {
    print_header "Setting Up Directories"
    
    # Create results directory if it doesn't exist
    if [[ ! -d "$RESULTS_DIR" ]]; then
        mkdir -p "$RESULTS_DIR"
        print_status "$BLUE" "📁 Created results directory: $RESULTS_DIR"
    fi
    
    # Create archive directory if it doesn't exist
    if [[ ! -d "$ARCHIVE_DIR" ]]; then
        mkdir -p "$ARCHIVE_DIR"
        print_status "$BLUE" "📁 Created archive directory: $ARCHIVE_DIR"
    fi
    
    print_status "$GREEN" "✅ Directories are ready"
}

# Function to get git information
get_git_info() {
    print_header "Git Information"
    
    if [[ -d "$PROJECT_ROOT/.git" ]]; then
        local current_branch
        local last_commit
        local commit_hash
        
        current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        last_commit=$(git log -1 --format="%an - %s" 2>/dev/null || echo "unknown")
        commit_hash=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
        
        print_status "$BLUE" "🌿 Current branch: $current_branch"
        print_status "$BLUE" "📝 Last commit: $last_commit"
        print_status "$BLUE" "🔗 Commit hash: $commit_hash"
        
        # Save git info to file
        cat > "$RESULTS_DIR/git_info.txt" << EOF
Git Information for Test Run: $TIMESTAMP
==========================================
Branch: $current_branch
Last Commit: $last_commit
Commit Hash: $commit_hash
EOF
        
    else
        print_status "$YELLOW" "⚠️  Not a git repository"
    fi
}

# Function to run pytest with comprehensive options
run_pytests() {
    print_header "Running Pytest Suite"
    
    local pytest_args=(
        "--verbose"
        "--tb=short"
        "--strict-markers"
        "--disable-warnings"
        "--color=yes"
        "--durations=10"
        "--maxfail=0"
        "--junit-xml=$RESULTS_DIR/${REPORT_NAME}.xml"
        "--capture=tee-sys"
        "tests/"
    )
    
    print_status "$BLUE" "🚀 Starting pytest with options: ${pytest_args[*]}"
    echo "Command: pytest ${pytest_args[*]}"
    echo
    
    # Run pytest and capture output
    if pytest "${pytest_args[@]}" 2>&1 | tee "$RESULTS_DIR/${REPORT_NAME}_output.log"; then
        print_status "$GREEN" "✅ Pytest completed successfully"
        return 0
    else
        local exit_code=$?
        print_status "$RED" "❌ Pytest failed with exit code: $exit_code"
        return $exit_code
    fi
}

# Function to generate summary report
generate_summary_report() {
    print_header "Generating Summary Report"
    
    local summary_file="$RESULTS_DIR/${REPORT_NAME}_summary.txt"
    
    # Extract test results from XML if it exists
    if [[ -f "$RESULTS_DIR/${REPORT_NAME}.xml" ]]; then
        local total_tests
        local failures
        local errors
        local skipped
        
        # Parse XML for test counts from testsuite attributes
        local testsuite_line
        testsuite_line=$(grep 'testsuite.*tests=' "$RESULTS_DIR/${REPORT_NAME}.xml" 2>/dev/null || echo "")
        
        if [[ -n "$testsuite_line" ]]; then
            # Extract values using regex
            total_tests=$(echo "$testsuite_line" | grep -o 'tests="[^"]*"' | cut -d'"' -f2 || echo "0")
            failures=$(echo "$testsuite_line" | grep -o 'failures="[^"]*"' | cut -d'"' -f2 || echo "0")
            errors=$(echo "$testsuite_line" | grep -o 'errors="[^"]*"' | cut -d'"' -f2 || echo "0")
            skipped=$(echo "$testsuite_line" | grep -o 'skipped="[^"]*"' | cut -d'"' -f2 || echo "0")
        else
            # Fallback to counting elements
            total_tests=$(grep -c "<testcase" "$RESULTS_DIR/${REPORT_NAME}.xml" 2>/dev/null || echo "0")
            failures=$(grep -c 'failure' "$RESULTS_DIR/${REPORT_NAME}.xml" 2>/dev/null || echo "0")
            errors=$(grep -c 'error' "$RESULTS_DIR/${REPORT_NAME}.xml" 2>/dev/null || echo "0")
            skipped=$(grep -c 'skipped' "$RESULTS_DIR/${REPORT_NAME}.xml" 2>/dev/null || echo "0")
        fi
        
        # Ensure we have valid numbers
        total_tests=${total_tests:-0}
        failures=${failures:-0}
        errors=${errors:-0}
        skipped=${skipped:-0}
        
        # Calculate passed tests
        local passed=$((total_tests - failures - errors - skipped))
        
        # Generate summary
        cat > "$summary_file" << EOF
Pytest Summary Report
=====================
Timestamp: $TIMESTAMP
Total Tests: $total_tests
Passed: $passed
Failed: $failures
Errors: $errors
Skipped: $skipped
Success Rate: $(( (passed * 100) / total_tests ))%

Test Results:
- ✅ Passed: $passed
- ❌ Failed: $failures
- ⚠️  Errors: $errors
- ⏭️  Skipped: $skipped

Files Generated:
- XML Report: ${REPORT_NAME}.xml
- Output Log: ${REPORT_NAME}_output.log
- Summary: ${REPORT_NAME}_summary.txt
- Git Info: git_info.txt

EOF
        
        print_status "$GREEN" "📊 Summary generated: $summary_file"
        print_status "$BLUE" "📈 Test Results: $passed/$total_tests passed ($(( (passed * 100) / total_tests ))%)"
        
    else
        print_status "$YELLOW" "⚠️  XML report not found, generating basic summary"
        
        cat > "$summary_file" << EOF
Pytest Summary Report
=====================
Timestamp: $TIMESTAMP
Note: XML report not available, check output log for details

Files Generated:
- Output Log: ${REPORT_NAME}_output.log
- Summary: ${REPORT_NAME}_summary.txt
- Git Info: git_info.txt

EOF
    fi
}

# Function to archive results
archive_results() {
    print_header "Archiving Test Results"
    
    local archive_file="$ARCHIVE_DIR/${REPORT_NAME}.tar.gz"
    
    # Create archive of current results
    if tar -czf "$archive_file" -C "$RESULTS_DIR" . 2>/dev/null; then
        print_status "$GREEN" "📦 Results archived to: $archive_file"
        
        # Get archive size
        local archive_size
        archive_size=$(du -h "$archive_file" | cut -f1)
        print_status "$BLUE" "📏 Archive size: $archive_size"
        
        # Clean up old archives (keep last 10)
        local archive_count
        archive_count=$(find "$ARCHIVE_DIR" -name "*.tar.gz" | wc -l)
        
        if [[ $archive_count -gt 10 ]]; then
            print_status "$YELLOW" "🧹 Cleaning up old archives (keeping last 10)..."
            find "$ARCHIVE_DIR" -name "*.tar.gz" -printf '%T@ %p\n' | sort -n | head -n $((archive_count - 10)) | cut -d' ' -f2- | xargs rm -f
            print_status "$GREEN" "✅ Cleanup completed"
        fi
        
    else
        print_status "$RED" "❌ Failed to create archive"
    fi
}

# Function to display final results
display_final_results() {
    print_header "Final Results Summary"
    
    echo -e "${GREEN}🎉 Pytest execution completed!${NC}"
    echo
    echo -e "${BLUE}📁 Results Location:${NC} $RESULTS_DIR"
    echo -e "${BLUE}📦 Archive Location:${NC} $ARCHIVE_DIR"
    echo
    echo -e "${BLUE}📋 Generated Files:${NC}"
    ls -la "$RESULTS_DIR" | grep "$REPORT_NAME" | while read -r line; do
        echo "   $line"
    done
    echo
    echo -e "${BLUE}🔗 Quick Access:${NC}"
    echo -e "   Summary: ${CYAN}$RESULTS_DIR/${REPORT_NAME}_summary.txt${NC}"
    echo -e "   XML Report: ${CYAN}$RESULTS_DIR/${REPORT_NAME}.xml${NC}"
    echo -e "   Output Log: ${CYAN}$RESULTS_DIR/${REPORT_NAME}_output.log${NC}"
    echo
    echo -e "${GREEN}✨ You can now review the test results and archive!${NC}"
}

# Function to cleanup temporary files
cleanup() {
    print_header "Cleanup"
    
    # Remove any temporary files if needed
    if [[ -f "/tmp/pytest_temp" ]]; then
        rm -f "/tmp/pytest_temp"
        print_status "$BLUE" "🧹 Cleaned up temporary files"
    fi
    
    print_status "$GREEN" "✅ Cleanup completed"
}

# Main execution function
main() {
    print_status "$BLUE" "🚀 Starting Comprehensive Pytest Runner and Archiver"
    echo "Project: $PROJECT_ROOT"
    echo "Timestamp: $TIMESTAMP"
    echo "Results Directory: $RESULTS_DIR"
    
    # Check dependencies
    check_dependencies
    
    # Setup directories
    setup_directories
    
    # Get git information
    get_git_info
    
    # Run pytest
    if run_pytests; then
        print_status "$GREEN" "✅ All tests passed!"
    else
        print_status "$YELLOW" "⚠️  Some tests failed - check the reports for details"
    fi
    
    # Generate summary
    generate_summary_report
    
    # Archive results
    archive_results
    
    # Display final results
    display_final_results
    
    # Cleanup
    cleanup
}

# Trap to handle script interruption
trap 'echo -e "\n\n⏹️  Pytest execution interrupted by user"; cleanup; exit 1' INT

# Run main function
main "$@"
