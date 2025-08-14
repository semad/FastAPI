"""Configuration and fixtures for API tests."""

import sys
import pytest
#from unittest.mock import AsyncMock, patch
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import environment loader to ensure variables are loaded
import env_loader

from fastapi.testclient import TestClient

@pytest.fixture(scope="function")
def client() -> TestClient:
    """Create a fresh test client for each test using the real FastAPI app."""
    # Import the real FastAPI application
    from app.main import app
    return TestClient(app)

# @pytest.fixture(autouse=True)
# def mock_cache_client():
#     """Mock the cache client to prevent MissingClientError in tests."""
#     # Create an async mock for the cache client since it's used with await
#     mock_client = AsyncMock()
#     mock_client.get.return_value = None  # No cached data
#     mock_client.set.return_value = None
#     mock_client.delete.return_value = None
#     mock_client.expire.return_value = None
    
#     # Mock the cache client without importing src modules
#     with patch('app.core.utils.cache.client', mock_client):
#         yield
