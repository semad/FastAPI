# PDF Import Script

This script automatically discovers PDF files in a directory structure and creates book entries in the FastAPI database using the CRUD API.

## Features

- **Recursive Directory Scanning**: Automatically traverses all subdirectories
- **PDF Detection**: Identifies PDF files by extension
- **Metadata Extraction**: Automatically extracts title and author from filenames
- **File Analysis**: Calculates file size and generates SHA-256 content hash
- **Duplicate Prevention**: Checks for existing books using content hash
- **API Integration**: Uses FastAPI CRUD endpoints for database operations
- **Progress Tracking**: Real-time progress updates and statistics
- **Error Handling**: Comprehensive error handling and reporting
- **Dry Run Mode**: Test mode without making database changes

## Requirements

- Python 3.7+
- FastAPI server running
- `aiohttp` library for HTTP requests
- Valid user account in the system

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r scripts/requirements_pdf_import.txt
   ```

2. **Make Script Executable** (optional):
   ```bash
   chmod +x scripts/import_pdfs.sh
   ```

## Usage

### Basic Usage

```bash
# Import PDFs from current directory
python scripts/import_pdfs.py .

# Import PDFs from specific directory
python scripts/import_pdfs.py /path/to/books

# Using the shell wrapper
./scripts/import_pdfs.sh /path/to/books
```

### Advanced Options

```bash
# Custom API endpoint
python scripts/import_pdfs.py /path/to/books --api-url http://localhost:8000

# Custom username
python scripts/import_pdfs.py /path/to/books --username admin

# Dry run (no database changes)
python scripts/import_pdfs.py /path/to/books --dry-run

# Combine options
python scripts/import_pdfs.py /path/to/books --api-url http://localhost:8000 --username admin --dry-run
```

### Shell Wrapper

The shell wrapper provides additional features:

```bash
# Show help
./scripts/import_pdfs.sh --help

# Basic usage
./scripts/import_pdfs.sh /path/to/books

# With options
./scripts/import_pdfs.sh /path/to/books --dry-run --username admin
```

## How It Works

### 1. Directory Scanning
- Recursively traverses the specified directory
- Skips hidden directories and system folders
- Identifies PDF files by `.pdf` extension

### 2. File Analysis
- Extracts file size in bytes
- Generates SHA-256 hash of file content
- Records relative path for database storage

### 3. Metadata Extraction
The script attempts to extract book title and author from filenames using common patterns:

**Supported Patterns**:
- `Title - Author.pdf`
- `Author - Title.pdf`
- `Title by Author.pdf`
- `Title_by_Author.pdf`
- `Title.pdf` (author set to "Unknown Author")

### 4. Database Integration
- Checks for existing books using content hash
- Creates new book entries via FastAPI CRUD API
- Handles errors gracefully with detailed reporting

### 5. Progress Tracking
- Real-time progress updates
- Comprehensive statistics at completion
- Error count and details

## Output Example

```
🚀 PDF Import Script
📁 Directory: /Users/username/Documents/Books
🌐 API URL: http://localhost:8000
👤 Username: admin
🔍 Mode: Live Import
--------------------------------------------------
🔍 Scanning directory: /Users/username/Documents/Books
📖 Processing PDF: The Great Gatsby - F. Scott Fitzgerald.pdf
✅ Created book: The Great Gatsby by F. Scott Fitzgerald (ID: 123)
📖 Processing PDF: 1984 - George Orwell.pdf
✅ Created book: 1984 by George Orwell (ID: 124)
📖 Processing PDF: sample_document.pdf
⚠️  Book already exists (hash: a1b2c3d4...): sample_document.pdf

==================================================
📊 IMPORT STATISTICS
==================================================
Total files scanned: 15
PDF files found: 3
Books created: 2
Books skipped (duplicates): 1
Errors: 0
==================================================
```

## Configuration

### Environment Variables
The script uses the following default values:
- **API URL**: `http://localhost:8000`
- **Username**: `admin`

### Customization
You can customize these values using command-line options or by modifying the script defaults.

## Error Handling

The script handles various error scenarios:

- **Permission Errors**: Skips directories with access restrictions
- **Network Errors**: Retries API calls with error reporting
- **Validation Errors**: Reports API validation failures
- **Duplicate Detection**: Automatically skips existing books

## File Naming Recommendations

For best results, use descriptive filenames:

**Good Examples**:
- `The Great Gatsby - F. Scott Fitzgerald.pdf`
- `1984 by George Orwell.pdf`
- `Pride and Prejudice - Jane Austen.pdf`

**Avoid**:
- `document1.pdf`
- `book.pdf`
- `untitled.pdf`

## Troubleshooting

### Common Issues

1. **Import Errors**: Check if FastAPI server is running
2. **Permission Errors**: Ensure script has read access to target directory
3. **Network Errors**: Verify API endpoint is accessible
4. **Authentication Errors**: Confirm username exists and has permissions

### Debug Mode

For detailed debugging, you can modify the script to add more verbose logging.

## Security Considerations

- The script requires valid user credentials
- Content hashes are generated locally (no file content sent to server)
- File paths are sanitized before database storage
- No file content is transmitted over the network

## Performance

- **File Hashing**: Uses chunked reading for large files
- **API Calls**: Asynchronous HTTP requests for better performance
- **Memory Usage**: Minimal memory footprint for large directory structures
- **Progress Updates**: Real-time feedback without blocking operations

## Contributing

To extend the script functionality:

1. **Add New File Types**: Modify `is_pdf_file()` method
2. **Enhance Metadata Extraction**: Extend `extract_book_metadata()` method
3. **Custom API Endpoints**: Modify API call methods
4. **Additional Validation**: Add custom validation logic

## License

This script is part of the FastAPI project and follows the same licensing terms.
