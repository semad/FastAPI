# Database Cleanup Tools for Testing

This directory contains tools to automatically clean up the test database before running tests, ensuring a clean state and avoiding constraint violations.

## Problem

The tests were failing due to database constraint violations because:
- Tests were trying to create records with duplicate unique values (ISBNs, emails, tier names)
- Previous test runs left data in the database
- Test isolation was not properly maintained

## Solution

We've created automated database cleanup tools that:
1. **Clean the database** before running tests
2. **Verify cleanup** was successful
3. **Run tests** with a guaranteed clean state

## Files

### Core Cleanup Scripts

- **`cleanup_db.py`** - Python script that cleans the database
- **`cleanup_db.sh`** - Shell script wrapper for the cleanup script

### Enhanced Test Runners

- **`run_tests_with_cleanup.py`** - Python test runner with automatic cleanup
- **`run_tests_clean.sh`** - Shell script wrapper for the enhanced test runner

## Usage

### Option 1: Clean Database Only

```bash
# Clean the database manually
./tests_db/cleanup_db.sh

# Or run the Python script directly
python3 tests_db/cleanup_db.py
```

### Option 2: Run Tests with Automatic Cleanup (Recommended)

```bash
# Run all tests with automatic cleanup
./tests_db/run_tests_clean.sh

# Run specific model tests with cleanup
./tests_db/run_tests_clean.sh --models user,book

# Run with verbose output and cleanup
./tests_db/run_tests_clean.sh --verbose

# Run with coverage and cleanup
./tests_db/run_tests_clean.sh --coverage

# Skip cleanup (not recommended)
./tests_db/run_tests_clean.sh --skip-cleanup
```

### Option 3: Python Scripts Directly

```bash
# Run the enhanced test runner directly
python3 tests_db/run_tests_with_cleanup.py --verbose

# List available models
python3 tests_db/run_tests_with_cleanup.py --list-models
```

## How It Works

1. **Database Cleanup Process**:
   - Connects to the PostgreSQL database
   - Identifies all user tables (excludes system tables)
   - Temporarily disables foreign key constraints
   - Truncates all tables (faster than DELETE, resets sequences)
   - Re-enables foreign key constraints
   - Verifies cleanup was successful

2. **Test Execution**:
   - Runs database cleanup automatically
   - Executes pytest with specified options
   - Provides clear feedback on success/failure

## Database Connection

The cleanup script connects to:
- **Host**: localhost
- **Port**: 5432
- **Database**: sqlapi
- **Username**: postgres
- **Password**: postgres

Make sure your PostgreSQL instance is running and accessible with these credentials.

## Safety Features

- **Excludes system tables** (pg_*, sql_*, alembic_version)
- **Temporary constraint disabling** (only during cleanup)
- **Error handling** with detailed logging
- **Verification step** to confirm cleanup success
- **Rollback capability** if cleanup fails

## Troubleshooting

### Common Issues

1. **Connection Failed**:
   - Ensure PostgreSQL is running
   - Check connection credentials
   - Verify database exists

2. **Permission Denied**:
   - Ensure postgres user has proper permissions
   - Check if database is accessible

3. **Cleanup Failed**:
   - Check database logs for errors
   - Verify no active connections are blocking cleanup
   - Try running cleanup manually first

### Manual Cleanup

If automated cleanup fails, you can manually clean the database:

```sql
-- Connect to your database and run:
TRUNCATE TABLE "user" CASCADE;
TRUNCATE TABLE book CASCADE;
TRUNCATE TABLE post CASCADE;
TRUNCATE TABLE tier CASCADE;
TRUNCATE TABLE rate_limit CASCADE;
-- Add other tables as needed
```

## Benefits

- ✅ **Eliminates constraint violations** from duplicate data
- ✅ **Ensures test isolation** between runs
- ✅ **Automated process** - no manual intervention needed
- ✅ **Fast execution** using TRUNCATE instead of DELETE
- ✅ **Safe operation** with proper error handling
- ✅ **Verification** that cleanup was successful

## Example Output

```
🧹 FastAPI Test Database Cleanup
=================================
Project: /Users/shahram/src/FastAPI
Script: /Users/shahram/src/FastAPI/tests_db/cleanup_db.py

🚀 Starting database cleanup...
🧹 Starting database cleanup...
📋 Found 5 tables to clean: book, post, rate_limit, tier, user
✅ Cleaned table: book
✅ Cleaned table: post
✅ Cleaned table: rate_limit
✅ Cleaned table: tier
✅ Cleaned table: user
🎉 Database cleanup completed successfully!
🔍 Verifying database cleanup...
✅ All tables are empty - cleanup successful!
🚀 Database is ready for testing!
```

Now you can run your tests with confidence that they'll start with a clean database state!
