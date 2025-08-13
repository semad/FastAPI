#!/usr/bin/env python

# This script creates the first superuser and the first tier in the FastAPI app.
# It mimics the docker-compose.yml "create_superuser" and "create_tier" service commands.

import os
import sys
import subprocess

def run_create_superuser():
    print("🚀 Creating first superuser...")
    # Run the script as a module with proper PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    
    result = subprocess.run(
        [sys.executable, "-m", "src.scripts.create_first_superuser"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env
    )
    if result.returncode == 0:
        print("✅ First superuser created successfully.")
    else:
        print("❌ Failed to create first superuser.")
        sys.exit(result.returncode)

def run_create_tier():
    print("🚀 Creating first tier...")
    # Run the script as a module with proper PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    
    result = subprocess.run(
        [sys.executable, "-m", "src.scripts.create_first_tier"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env
    )
    if result.returncode == 0:
        print("✅ First tier created successfully.")
    else:
        print("❌ Failed to create first tier.")
        sys.exit(result.returncode)

if __name__ == "__main__":
    run_create_superuser()
    run_create_tier()
