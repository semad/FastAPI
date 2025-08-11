#!/bin/bash

# PDF Import Script Wrapper
# This script provides an easy way to run the PDF import functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🚀 PDF Import Script Wrapper${NC}"
echo -e "${BLUE}========================${NC}"

# Check if we're in the right directory
if [[ ! -f "$PROJECT_ROOT/src/app/main.py" ]]; then
    echo -e "${RED}❌ Error: This script must be run from the FastAPI project root directory${NC}"
    echo -e "${YELLOW}   Expected: $PROJECT_ROOT/src/app/main.py${NC}"
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Error: Python is not installed or not in PATH${NC}"
    exit 1
fi

# Check if required packages are installed
echo -e "${BLUE}📦 Checking dependencies...${NC}"
if ! python -c "import aiohttp" &> /dev/null; then
    echo -e "${YELLOW}⚠️  aiohttp not found. Installing dependencies...${NC}"
    pip install -r "$SCRIPT_DIR/requirements_pdf_import.txt"
fi

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage:${NC}"
    echo -e "  $0 <directory> [options]"
    echo ""
    echo -e "${BLUE}Arguments:${NC}"
    echo -e "  directory    Directory to scan for PDF files"
    echo ""
    echo -e "${BLUE}Options:${NC}"
    echo -e "  --api-url <url>     FastAPI server URL (default: http://localhost:8000)"
    echo -e "  --username <user>   Username for book creation (default: admin)"
    echo -e "  --dry-run           Scan files without creating books (dry run mode)"
    echo -e "  --help              Show this help message"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo -e "  $0 .                           # Import PDFs from current directory"
    echo -e "  $0 /path/to/books             # Import PDFs from specific directory"
    echo -e "  $0 . --dry-run                # Dry run mode"
    echo -e "  $0 . --username admin         # Use specific username"
    echo -e "  $0 . --api-url http://localhost:8000  # Use custom API URL"
}

# Parse arguments
if [[ $# -eq 0 ]]; then
    show_usage
    exit 1
fi

# Check for help
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_usage
    exit 0
fi

# Get directory
DIRECTORY="$1"
shift

# Build Python command
PYTHON_CMD="python $SCRIPT_DIR/import_pdfs.py \"$DIRECTORY\""

# Add additional arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --api-url)
            PYTHON_CMD="$PYTHON_CMD --api-url \"$2\""
            shift 2
            ;;
        --username)
            PYTHON_CMD="$PYTHON_CMD --username \"$2\""
            shift 2
            ;;
        --dry-run)
            PYTHON_CMD="$PYTHON_CMD --dry-run"
            shift
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Change to project root
cd "$PROJECT_ROOT"

echo -e "${BLUE}📁 Project root: $PROJECT_ROOT${NC}"
echo -e "${BLUE}🔍 Target directory: $DIRECTORY${NC}"
echo -e "${BLUE}🐍 Python command: $PYTHON_CMD${NC}"
echo ""

# Run the Python script
echo -e "${GREEN}🚀 Starting PDF import...${NC}"
echo -e "${YELLOW}Press Ctrl+C to interrupt at any time${NC}"
echo ""

eval $PYTHON_CMD

echo ""
echo -e "${GREEN}✅ PDF import completed!${NC}"
