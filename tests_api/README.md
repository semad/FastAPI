# API Tests for FastAPI Application

This directory contains API tests for the FastAPI application. These tests focus on testing HTTP endpoints rather than direct CRUD operations.

## 🏗️ Directory Structure

```
tests_api/
├── conftest.py              # Test configuration and fixtures
├── helpers/                  # Helper utilities for API tests
│   ├── __init__.py
│   └── api_helpers.py       # Common helper functions
├── api/                      # API endpoint tests
│   └── v1/                  # API version 1 tests
│       └── test_books.py    # Book endpoint tests
├── health_check.py          # Health check script for API service
├── health_check.sh          # Health check shell script wrapper
├── run_api_tests.py         # Python test runner
├── run_api_tests.sh         # Shell script wrapper
└── README.md                # This file
```

## 🎯 What API Tests Cover

### **Authentication & Authorization**
- ✅ Unauthorized access (401 responses)
- ✅ Authorized access with valid tokens
- ✅ Role-based access control (superuser vs regular user)

### **HTTP Endpoints**
- ✅ GET endpoints (list, retrieve)
- ✅ POST endpoints (create)
- ✅ PATCH endpoints (update)
- ✅ DELETE endpoints (delete)
- ✅ Search and filtering
- ✅ Pagination

### **Response Validation**
- ✅ HTTP status codes
- ✅ Response structure
- ✅ Data validation
- ✅ Error handling

### **Data Flow**
- ✅ Create → Read → Update → Delete workflow
- ✅ Relationship testing
- ✅ Constraint validation

## 🚀 Running API Tests

### **Run All API Tests**
```bash
# Using Python directly
python tests_api/run_api_tests.py

# Using shell script
./tests_api/run_api_tests.sh
```

## 🏥 Health Checking

### **Check API Service Health**
```bash
# Basic health check
python tests_api/health_check.py

# Using shell script
./tests_api/health_check.sh

# Verbose output with details
./tests_api/health_check.sh --verbose

# Check specific URL
./tests_api/health_check.sh --url http://localhost:8000

# Custom timeout
./tests_api/health_check.sh --timeout 30
```

The health check script verifies:
- ✅ **Service connectivity** and response times
- ✅ **OpenAPI documentation** accessibility
- ✅ **API schema** and available endpoints
- ✅ **Health/ready endpoints** (if implemented)
- 📊 **Overall service status** and success rate

### **Run Specific Model Tests**
```bash
# Test only book endpoints
python tests_api/run_api_tests.py --models books

# Test multiple models
python tests_api/run_api_tests.py --models books posts users
```

### **Verbose Output**
```bash
python tests_api/run_api_tests.py --verbose
```

### **Help**
```bash
python tests_api/run_api_tests.py --help
```

## 🔧 Test Configuration

### **Database Setup**
- Uses the same test database as CRUD tests
- Each test gets a fresh database session
- Automatic cleanup between tests

### **Authentication**
- `test_user` fixture: Regular user with JWT token
- `test_superuser` fixture: Superuser with JWT token
- `auth_headers` fixture: Headers with user token
- `superuser_auth_headers` fixture: Headers with superuser token

### **Test Client**
- `client` fixture: FastAPI TestClient instance
- `async_db` fixture: Async database session

## 📝 Writing New API Tests

### **1. Create Test File**
Create a new test file in `tests_api/api/v1/` following the naming convention:
```python
# tests_api/api/v1/test_posts.py
"""API tests for post endpoints."""

import pytest
from fastapi.testclient import TestClient

from tests_api.conftest import client, auth_headers
from tests_api.helpers.api_helpers import generate_post_data, assert_response_structure


class TestPostEndpoints:
    """Test post API endpoints."""
    
    def test_get_posts_unauthorized(self, client: TestClient):
        """Test that unauthorized users cannot access posts."""
        response = client.get("/api/v1/posts/")
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_get_posts_authorized(self, client: TestClient, auth_headers: dict):
        """Test that authorized users can access posts."""
        response = client.get("/api/v1/posts/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "total_count" in data
```

### **2. Use Helper Functions**
```python
from tests_api.helpers.api_helpers import generate_post_data, assert_response_structure

# Generate test data
post_data = generate_post_data()

# Validate response structure
assert_response_structure(data, ["id", "title", "text", "created_at"])
```

### **3. Test Authentication Patterns**
```python
def test_endpoint_unauthorized(self, client: TestClient):
    """Test unauthorized access."""
    response = client.get("/api/v1/endpoint/")
    assert response.status_code == 401

def test_endpoint_authorized(self, client: TestClient, auth_headers: dict):
    """Test authorized access."""
    response = client.get("/api/v1/endpoint/", headers=auth_headers)
    assert response.status_code == 200
```

## 🔍 Test Patterns

### **CRUD Workflow Testing**
```python
def test_full_crud_workflow(self, client: TestClient, auth_headers: dict):
    """Test complete CRUD workflow."""
    # 1. Create
    data = generate_post_data()
    create_response = client.post("/api/v1/posts/", json=data, headers=auth_headers)
    assert create_response.status_code == 201
    created_post = create_response.json()
    
    # 2. Read
    post_id = created_post["id"]
    read_response = client.get(f"/api/v1/posts/{post_id}", headers=auth_headers)
    assert read_response.status_code == 200
    
    # 3. Update
    update_data = {"title": "Updated Title"}
    update_response = client.patch(f"/api/v1/posts/{post_id}", json=update_data, headers=auth_headers)
    assert update_response.status_code == 200
    
    # 4. Delete
    delete_response = client.delete(f"/api/v1/posts/{post_id}", headers=auth_headers)
    assert delete_response.status_code == 204
```

### **Error Handling Testing**
```python
def test_validation_errors(self, client: TestClient, auth_headers: dict):
    """Test input validation errors."""
    invalid_data = {"title": ""}  # Empty title
    response = client.post("/api/v1/posts/", json=invalid_data, headers=auth_headers)
    assert response.status_code == 422
    assert "detail" in response.json()

def test_not_found_errors(self, client: TestClient, auth_headers: dict):
    """Test not found errors."""
    response = client.get("/api/v1/posts/99999", headers=auth_headers)
    assert response.status_code == 404
```

## 🧹 Test Cleanup

- Each test runs in isolation
- Database changes are automatically rolled back
- No test data persists between tests
- Clean authentication tokens for each test

## 🔗 Integration with CRUD Tests

- **CRUD Tests** (`tests_db/`): Test database operations directly
- **API Tests** (`tests_api/`): Test HTTP endpoints and integration
- Both use the same test database
- Both benefit from the same cleanup system

## 📊 Test Results

API tests provide a different perspective on application health:
- ✅ **CRUD Tests**: Verify data layer works correctly
- ✅ **API Tests**: Verify HTTP layer works correctly
- ✅ **Combined**: Full-stack application validation

## 🚨 Troubleshooting

### **Common Issues**

1. **Import Errors**: Ensure you're importing from `tests_api.conftest`
2. **Database Issues**: Check that the test database is running
3. **Authentication Errors**: Verify JWT token generation is working
4. **Endpoint Not Found**: Check that the API routes are properly configured

### **Debug Mode**
```bash
# Run with maximum verbosity
python tests_api/run_api_tests.py -vvv

# Run specific test with print statements
python -m pytest tests_api/api/v1/test_books.py::TestBookEndpoints::test_create_book_authorized -v -s
```

## 🎯 Next Steps

1. **Add More Endpoint Tests**: Create tests for posts, users, tiers, etc.
2. **Performance Testing**: Add load testing for critical endpoints
3. **Security Testing**: Add tests for edge cases and security vulnerabilities
4. **Integration Testing**: Test with external services and databases
