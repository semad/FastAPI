#!/usr/bin/env python3
"""
API Test Runner for FastAPI Application

This script runs API tests for the FastAPI application, testing HTTP endpoints
rather than direct CRUD operations.

Usage:
    python tests_api/run_api_tests.py                    # Run all API tests
    python tests_api/run_api_tests.py --models books     # Run only book API tests
    python tests_api/run_api_tests.py --models posts     # Run only post API tests
    python tests_api/run_api_tests.py --verbose          # Run with verbose output
    python tests_api/run_api_tests.py --help             # Show help
"""

import click
import os
import subprocess
import sys
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    current_dir = Path(__file__).parent
    return current_dir.parent


def run_api_tests(models=None, verbose=False):
    """Run API tests with the specified options."""
    project_root = get_project_root()
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    # Change to tests_api directory and run pytest
    os.chdir(project_root / "tests_api")
    
    # Add test discovery
    cmd.append(".")
    
    # Add specific model tests if specified
    if models:
        for model in models:
            test_file = f"api/v1/test_{model}.py"
            if os.path.exists(test_file):
                cmd.append(test_file)
            else:
                click.echo(f"⚠️  Warning: Test file {test_file} not found")
    
    click.echo(f"🚀 Running API Tests")
    click.echo(f"Project: {project_root}")
    click.echo(f"Command: {' '.join(cmd)}")
    click.echo("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        click.echo("\n❌ Test execution interrupted by user")
        return 1
    except Exception as e:
        click.echo(f"❌ Error running tests: {e}")
        return 1


@click.command(
    name="run-api-tests",
    help="Run API tests for FastAPI application",
    epilog="""
Examples:
    python tests_api/run_api_tests.py                    # Run all API tests
    python tests_api/run_api_tests.py --models books     # Run only book API tests
    python tests_api/run_api_tests.py --models posts     # Run only post API tests
    python tests_api/run_api_tests.py --verbose          # Run with verbose output
    """
)
@click.option(
    "--models",
    "-m",
    multiple=True,
    help="Specific models to test (e.g., books posts users). Can be specified multiple times."
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Run tests with verbose output"
)
def main(models, verbose):
    """Run API tests for FastAPI application.
    
    This script runs API tests for the FastAPI application, testing HTTP endpoints
    rather than direct CRUD operations.
    
    If no models are specified, all available tests will be run.
    """
    # Run the tests
    exit_code = run_api_tests(
        models=models,
        verbose=verbose
    )
    
    if exit_code == 0:
        click.echo("\n✅ All API tests passed successfully!")
    else:
        click.echo(f"\n❌ Some API tests failed (exit code: {exit_code})")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
