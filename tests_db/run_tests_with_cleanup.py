#!/usr/bin/env python3
"""
Enhanced test runner with automatic database cleanup.

This script automatically cleans up the database before running tests
to ensure a clean state and avoid constraint violations.
"""

import argparse
import subprocess
import sys
import os
import asyncio
from pathlib import Path
from typing import List, Optional

# Import the cleanup function
from cleanup_db import cleanup_database, verify_cleanup

def get_test_files() -> List[str]:
    """Get all test files in the tests_db directory."""
    tests_dir = Path(__file__).parent
    test_files = []
    
    for test_file in tests_dir.glob("test_*.py"):
        if test_file.name != "__init__.py":
            test_files.append(str(test_file))
    
    return sorted(test_files)

def get_model_names() -> List[str]:
    """Extract model names from test file names."""
    test_files = get_test_files()
    model_names = []
    
    for test_file in test_files:
        # Extract model name from test_*.py filename
        filename = os.path.basename(test_file)
        model_name = filename.replace("test_", "").replace(".py", "")
        model_names.append(model_name)
    
    return model_names

async def run_database_cleanup():
    """Run database cleanup before tests."""
    print("🧹 Running database cleanup...")
    try:
        await cleanup_database()
        await verify_cleanup()
        print("✅ Database cleanup completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Database cleanup failed: {e}")
        return False

def run_tests_for_models(models: Optional[List[str]] = None, verbose: bool = False, coverage: bool = False, skip_cleanup: bool = False) -> int:
    """Run tests for specified models or all models if none specified."""
    if models is None:
        models = get_model_names()
    
    print(f"Running tests for models: {', '.join(models)}")
    print("=" * 60)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src/app/models", "--cov-report=html", "--cov-report=term-missing"])
    
    # Add test files for specified models
    for model in models:
        test_file = f"tests_db/test_{model}.py"
        if os.path.exists(test_file):
            cmd.append(test_file)
        else:
            print(f"Warning: Test file {test_file} not found for model {model}")
    
    # Add conftest.py and helpers
    cmd.extend(["tests_db/conftest.py", "tests_db/helpers/"])
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        # Run the tests
        result = subprocess.run(cmd, check=False, capture_output=False)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install pytest: pip install pytest pytest-asyncio")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

async def main():
    """Main function to parse arguments and run tests with cleanup."""
    parser = argparse.ArgumentParser(
        description="Run unit tests with automatic database cleanup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests_db/run_tests_with_cleanup.py                    # Run all tests with cleanup
  python tests_db/run_tests_with_cleanup.py --verbose          # Run with verbose output
  python tests_db/run_tests_with_cleanup.py --coverage         # Run with coverage report
  python tests_db/run_tests_with_cleanup.py --models user,book # Run tests for specific models only
  python tests_db/run_tests_with_cleanup.py --skip-cleanup     # Skip database cleanup
        """
    )
    
    parser.add_argument(
        "--models",
        help="Comma-separated list of models to test (e.g., user,book,post)",
        type=str
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests with verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List all available models and exit"
    )
    
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Skip database cleanup before running tests"
    )
    
    args = parser.parse_args()
    
    if args.list_models:
        models = get_model_names()
        print("Available models for testing:")
        for model in models:
            print(f"  - {model}")
        return 0
    
    # Parse models argument
    models = None
    if args.models:
        models = [m.strip() for m in args.models.split(",")]
        
        # Validate model names
        available_models = get_model_names()
        invalid_models = [m for m in models if m not in available_models]
        if invalid_models:
            print(f"Error: Invalid model names: {', '.join(invalid_models)}")
            print(f"Available models: {', '.join(available_models)}")
            return 1
    
    # Run database cleanup if not skipped
    if not args.skip_cleanup:
        print("🔄 Preparing database for testing...")
        cleanup_success = await run_database_cleanup()
        if not cleanup_success:
            print("❌ Failed to clean database. Tests may fail due to constraint violations.")
            print("💡 You can use --skip-cleanup to bypass this step.")
            return 1
        print()
    else:
        print("⚠️  Skipping database cleanup (--skip-cleanup specified)")
        print("💡 Tests may fail due to existing data in the database.")
        print()
    
    # Run the tests
    return_code = run_tests_for_models(models, args.verbose, args.coverage)
    
    if return_code == 0:
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed. Please check the output above.")
    
    return return_code

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
