#!/bin/bash

# Template Script for FastAPI
# Use this as a starting point for new scripts

set -e  # Exit on any error

# Configuration
SCRIPT_NAME="$(basename "$0")"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Main function
main() {
    log_info "Starting $SCRIPT_NAME"
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Your script logic here
    log_info "Project root: $PROJECT_ROOT"
    
    log_success "Script completed successfully!"
}

# Run main function
main "$@"
