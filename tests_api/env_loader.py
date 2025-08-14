"""Environment variable loader for tests."""

import os
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file."""
    # The .env file is in the src directory
    env_path = Path(__file__).parent.parent / "src" / ".env"
    
    if env_path.exists():
        print(f"Loading environment variables from: {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value
                    # Mask sensitive values in output
                    if 'PASSWORD' in key or 'SECRET' in key:
                        print(f"Loaded: {key} = {value[:8]}...")
                    else:
                        print(f"Loaded: {key} = {value}")
        return True
    else:
        print(f"Environment file not found at: {env_path}")
        return False

# Load environment variables when module is imported
load_env_file()
