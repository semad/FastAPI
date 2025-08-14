# Bash Script Templates

This directory contains reusable bash script templates that demonstrate different approaches to command-line option processing.

## Available Templates

### 1. `template.sh` - Full-Featured Template with Long and Short Options

**Features:**
- Supports both long (--help) and short (-h) options
- Comprehensive option handling
- Built-in logging functions (debug, verbose, info, warn, error)
- Signal handling and cleanup
- Option validation
- Dry-run mode
- Force mode

**Usage:**
```bash
./template.sh --help                    # Show help
./template.sh --verbose --debug         # Enable verbose and debug
./template.sh -v -d -n                  # Short options with dry-run
./template.sh --config file.conf --output /tmp
```

**Common Options:**
- `-h, --help` - Show help message
- `-v, --verbose` - Enable verbose output
- `-d, --debug` - Enable debug mode
- `-q, --quiet` - Suppress output
- `-c, --config FILE` - Configuration file
- `-o, --output DIR` - Output directory
- `-n, --dry-run` - Show what would be done
- `-f, --force` - Force execution

### 2. `template_getopts.sh` - Traditional getopts Template

**Features:**
- Uses traditional `getopts` for single-letter options only
- Simpler implementation
- Standard bash approach
- Good for scripts that only need short options

**Usage:**
```bash
./template_getopts.sh -h               # Show help
./template_getopts.sh -v -d -q         # Enable verbose, debug, quiet
./template_getopts.sh -c config.conf -o /tmp
```

**Common Options:**
- `-h` - Show help message
- `-v` - Enable verbose output
- `-d` - Enable debug mode
- `-q` - Suppress output
- `-c FILE` - Configuration file
- `-o DIR` - Output directory
- `-n` - Dry-run mode
- `-f` - Force execution
- `-V` - Show version

## How to Use These Templates

### 1. Copy and Customize

```bash
# Copy the template you want to use
cp template.sh my_new_script.sh

# Make it executable
chmod +x my_new_script.sh

# Edit the script to add your logic
nano my_new_script.sh
```

### 2. Modify the Configuration Section

```bash
# Update these variables for your script
SCRIPT_NAME="my_script"
VERSION="1.0.0"

# Add your own default values
MY_OPTION=""
ANOTHER_OPTION=""
```

### 3. Add Your Own Options

For `template.sh` (long and short options):
```bash
# Add to the option parsing section
--my-option)
    MY_OPTION="$2"
    shift 2
    ;;
-m)
    MY_OPTION="$2"
    shift 2
    ;;
```

For `template_getopts.sh` (short options only):
```bash
# Add to the getopts string (add 'm:' for option with argument)
while getopts ":hvdqnc:o:Vnfm:" opt; do
    case $opt in
        m)
            MY_OPTION="$OPTARG"
            ;;
        # ... other cases
    esac
done
```

### 4. Add Your Logic

Replace the `process()` function with your actual script logic:

```bash
process() {
    debug "Starting my custom processing..."
    
    # Your custom logic here
    if [[ -n "$MY_OPTION" ]]; then
        info "Processing with option: $MY_OPTION"
        # Do something with MY_OPTION
    fi
    
    # Process additional arguments
    for arg in "$@"; do
        info "Processing argument: $arg"
        # Process each argument
    done
    
    debug "Processing complete"
}
```

## Best Practices

### 1. Error Handling
- Always use `set -euo pipefail` for robust error handling
- Validate options before processing
- Provide meaningful error messages
- Use appropriate exit codes

### 2. Logging
- Use the built-in logging functions (debug, verbose, info, warn, error)
- Respect the quiet mode setting
- Send debug and verbose messages to stderr
- Use consistent message formatting

### 3. Option Processing
- Always provide both long and short options when possible
- Validate required arguments
- Provide helpful error messages for missing arguments
- Use descriptive option names

### 4. Signal Handling
- Set up cleanup functions
- Handle interrupts gracefully
- Clean up temporary files and resources

### 5. Documentation
- Include comprehensive help text
- Document all options and arguments
- Provide usage examples
- Document exit codes

## Example Customization

Here's how you might customize `template.sh` for a file processing script:

```bash
# Add custom options
FILE_PATTERN="*.txt"
RECURSIVE=false
BACKUP=false

# Add to option parsing
--pattern)
    FILE_PATTERN="$2"
    shift 2
    ;;
--recursive)
    RECURSIVE=true
    shift
    ;;
--backup)
    BACKUP=true
    shift
    ;;

# Customize the process function
process() {
    debug "Processing files matching pattern: $FILE_PATTERN"
    
    if [[ "$RECURSIVE" == true ]]; then
        find . -name "$FILE_PATTERN" -exec process_file {} \;
    else
        for file in $FILE_PATTERN; do
            process_file "$file"
        done
    fi
}
```

## Exit Codes

Use these standard exit codes:
- `0` - Success
- `1` - General error
- `2` - Invalid option
- `3` - Missing required argument
- `4` - File not found
- `5` - Permission denied

## Testing Your Script

Always test your script with various option combinations:

```bash
# Test help and version
./my_script.sh --help
./my_script.sh --version

# Test option combinations
./my_script.sh --verbose --debug
./my_script.sh -v -d -q

# Test error conditions
./my_script.sh --invalid-option
./my_script.sh --config nonexistent.conf

# Test with arguments
./my_script.sh -v file1.txt file2.txt
```

These templates provide a solid foundation for creating professional, robust bash scripts with proper option handling and error management.
