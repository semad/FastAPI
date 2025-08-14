#!/usr/bin/env bash
#===============================================================================
# Script Template with Traditional getopts
#===============================================================================
# 
# This template demonstrates the traditional getopts approach for processing
# single-letter command-line options. This is simpler but only supports
# single-letter options.
#
# Usage:
#   ./template_getopts.sh [OPTIONS] [ARGUMENTS]
#
# Examples:
#   ./template_getopts.sh -h
#   ./template_getopts.sh -v -d -q
#   ./template_getopts.sh -c config.conf -o /tmp/output
#===============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

#===============================================================================
# Configuration
#===============================================================================
SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.0.0"

# Default values
VERBOSE=false
DEBUG=false
QUIET=false
CONFIG_FILE=""
OUTPUT_DIR=""
DRY_RUN=false
FORCE=false

#===============================================================================
# Functions
#===============================================================================

# Print usage information
usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS] [ARGUMENTS]

Description:
    This is a template script that demonstrates traditional getopts usage.

Options:
    -h          Show this help message and exit
    -v          Enable verbose output
    -d          Enable debug mode
    -q          Suppress output (quiet mode)
    -c FILE     Specify configuration file
    -o DIR      Specify output directory
    -n          Show what would be done without doing it
    -f          Force execution even if warnings exist
    -V          Show version information and exit

Examples:
    $SCRIPT_NAME -h
    $SCRIPT_NAME -v -d -q
    $SCRIPT_NAME -c config.conf -o /tmp/output
    $SCRIPT_NAME -c config.conf -o /tmp/output -n

Arguments:
    Additional arguments can be provided after options.

Exit Codes:
    0   Success
    1   General error
    2   Invalid option
    3   Missing required argument

EOF
}

# Print version information
version() {
    echo "$SCRIPT_NAME version $VERSION"
}

# Print debug message
debug() {
    if [[ "$DEBUG" == true ]]; then
        echo "[DEBUG] $*" >&2
    fi
}

# Print verbose message
verbose() {
    if [[ "$VERBOSE" == true ]]; then
        echo "[VERBOSE] $*" >&2
    fi
}

# Print info message
info() {
    if [[ "$QUIET" == false ]]; then
        echo "[INFO] $*" >&2
    fi
}

# Print error message and exit
error() {
    echo "[ERROR] $*" >&2
    exit 1
}

# Validate options
validate_options() {
    # Check if config file exists
    if [[ -n "$CONFIG_FILE" && ! -f "$CONFIG_FILE" ]]; then
        error "Configuration file not found: $CONFIG_FILE"
    fi
    
    # Check if output directory is writable
    if [[ -n "$OUTPUT_DIR" ]]; then
        if [[ ! -d "$OUTPUT_DIR" ]]; then
            if [[ "$FORCE" == true ]]; then
                verbose "Creating output directory: $OUTPUT_DIR"
                mkdir -p "$OUTPUT_DIR" || error "Failed to create output directory: $OUTPUT_DIR"
            else
                error "Output directory does not exist: $OUTPUT_DIR"
            fi
        elif [[ ! -w "$OUTPUT_DIR" ]]; then
            error "Output directory is not writable: $OUTPUT_DIR"
        fi
    fi
}

# Main processing function
process() {
    debug "Starting processing..."
    
    if [[ "$DRY_RUN" == true ]]; then
        info "DRY RUN MODE - No actual changes will be made"
    fi
    
    # Example processing logic
    info "Processing with options:"
    info "  Verbose: $VERBOSE"
    info "  Debug: $DEBUG"
    info "  Quiet: $QUIET"
    info "  Config: ${CONFIG_FILE:-'default'}"
    info "  Output: ${OUTPUT_DIR:-'default'}"
    info "  Dry Run: $DRY_RUN"
    info "  Force: $FORCE"
    
    # Process additional arguments
    if [[ $# -gt 0 ]]; then
        info "Additional arguments: $*"
    fi
    
    # Your main logic goes here
    debug "Processing complete"
}

#===============================================================================
# Main script
#===============================================================================

# Parse command line options using getopts
# The colon after an option means it requires an argument
# The colon at the beginning means silent error reporting
while getopts ":hvdqnc:o:Vnf" opt; do
    case $opt in
        h)
            usage
            exit 0
            ;;
        V)
            version
            exit 0
            ;;
        v)
            VERBOSE=true
            ;;
        d)
            DEBUG=true
            ;;
        q)
            QUIET=true
            ;;
        c)
            CONFIG_FILE="$OPTARG"
            ;;
        o)
            OUTPUT_DIR="$OPTARG"
            ;;
        n)
            DRY_RUN=true
            ;;
        f)
            FORCE=true
            ;;
        \?)
            error "Invalid option: -$OPTARG"
            ;;
        :)
            error "Option -$OPTARG requires an argument"
            ;;
    esac
done

# Shift to the remaining arguments
shift $((OPTIND-1))

# Validate options
validate_options

# Start processing
debug "Script started: $SCRIPT_NAME"
debug "Script directory: $SCRIPT_DIR"
debug "Arguments remaining: $*"

# Call main processing function with remaining arguments
process "$@"

# Success
info "Script completed successfully"
exit 0
