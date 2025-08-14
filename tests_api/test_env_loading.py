"""Test script to verify environment variable loading from .env file."""

import os
import sys
from pathlib import Path

# Import the environment loader to trigger loading
import env_loader

def test_env_loading():
    """Test that environment variables are loaded from .env file."""
    print("Testing environment variable loading...")
    
    # Check if key environment variables are loaded
    env_vars = [
        "API_ADMIN_USERNAME",
        "API_ADMIN_PASSWORD", 
        "API_ADMIN_EMAIL",
        "API_ADMIN_NAME",
        "SECRET_KEY",
        "DATABASE_URL"
    ]
    
    print("\nEnvironment variables:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "PASSWORD" in var or "SECRET" in var:
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                print(f"  {var}: {masked_value}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: NOT SET")
    
    # Test specific API_ADMIN values
    admin_username = os.getenv("API_ADMIN_USERNAME")
    admin_password = os.getenv("API_ADMIN_PASSWORD")
    
    if admin_username and admin_password:
        print(f"\n✅ API_ADMIN credentials loaded successfully:")
        print(f"   Username: {admin_username}")
        print(f"   Password: {admin_password[:8]}...")
    else:
        print("\n❌ API_ADMIN credentials not loaded!")
        return False
    
    return True

if __name__ == "__main__":
    success = test_env_loading()
    if success:
        print("\n🎉 Environment variable loading test passed!")
        sys.exit(0)
    else:
        print("\n💥 Environment variable loading test failed!")
        sys.exit(1)
