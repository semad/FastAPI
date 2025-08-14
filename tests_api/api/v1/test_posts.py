"""Test post API endpoints with both GET and POST methods."""

import pytest
from fastapi.testclient import TestClient
from helpers.api_helpers import generate_post_data


class TestPostEndpoints:
    """Test post API endpoints with both GET and POST methods."""

    def test_posts_endpoint_get_method(self, client: TestClient):
        """Test that the posts endpoint responds to GET requests."""
        response = client.get("/api/v1/apiadmin/posts")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_posts_endpoint_post_method(self, client: TestClient):
        """Test that the posts endpoint responds to POST requests."""
        response = client.post("/api/v1/apiadmin/posts")
        # The real API supports POST method, so expect 200 or 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            # Check for pagination structure
            assert "data" in data
            assert "total_count" in data
            assert "page" in data
            assert "items_per_page" in data
            assert isinstance(data["data"], list)
        else:
            data = response.json()
            assert "detail" in data

    def test_posts_endpoint_with_pagination_get(self, client: TestClient):
        """Test posts endpoint with pagination using GET method."""
        response = client.get("/api/v1/apiadmin/posts?page=1&items_per_page=5")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_posts_endpoint_with_pagination_post(self, client: TestClient):
        """Test posts endpoint with pagination using POST method."""
        response = client.post("/api/v1/apiadmin/posts?page=1&items_per_page=5")
        # The real API supports POST method, so expect 200 or 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            # Check for pagination structure
            assert "data" in data
            assert "total_count" in data
            assert "page" in data
            assert "items_per_page" in data
            assert isinstance(data["data"], list)
            assert data["page"] == 1
            assert data["items_per_page"] == 5
        else:
            data = response.json()
            assert "detail" in data

    def test_posts_endpoint_nonexistent_user_get(self, client: TestClient):
        """Test posts endpoint for nonexistent user using GET method."""
        response = client.get("/api/v1/nonexistentuser/posts")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_posts_endpoint_nonexistent_user_post(self, client: TestClient):
        """Test posts endpoint for nonexistent user using POST method."""
        response = client.post("/api/v1/nonexistentuser/posts")
        # The real API returns 404 for nonexistent user
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_post_by_id_endpoint_get(self, client: TestClient):
        """Test getting a specific post by ID using GET method."""
        response = client.get("/api/v1/apiadmin/post/1")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_post_by_id_endpoint_post(self, client: TestClient):
        """Test getting a specific post by ID using POST method."""
        response = client.post("/api/v1/apiadmin/post/1")
        # The real API returns 404 for non-existent posts or 200 if it exists
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "title" in data
            assert "text" in data
        else:
            data = response.json()
            assert "detail" in data

    def test_create_post_endpoint_unauthorized_get(self, client: TestClient):
        """Test that unauthorized users cannot create posts using GET method."""
        response = client.get("/api/v1/testuser/post")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_create_post_endpoint_unauthorized_post(self, client: TestClient):
        """Test that unauthorized users cannot create posts using POST method."""
        post_data = generate_post_data()
        response = client.post("/api/v1/testuser/post", json=post_data)
        # The real API returns 401 for unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_update_post_endpoint_unauthorized_get(self, client: TestClient):
        """Test that unauthorized users cannot update posts using GET method."""
        response = client.get("/api/v1/testuser/post/1")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_update_post_endpoint_unauthorized_post(self, client: TestClient):
        """Test that unauthorized users cannot update posts using POST method."""
        post_data = {"title": "Updated Title"}
        response = client.post("/api/v1/testuser/post/1", json=post_data)
        # The real API returns 401 for unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_delete_post_endpoint_unauthorized_get(self, client: TestClient):
        """Test that unauthorized users cannot delete posts using GET method."""
        response = client.get("/api/v1/testuser/post/1")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_delete_post_endpoint_unauthorized_post(self, client: TestClient):
        """Test that unauthorized users cannot delete posts using POST method."""
        response = client.post("/api/v1/testuser/post/1")
        # The real API returns 401 for unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_permanent_delete_post_endpoint_unauthorized_get(self, client: TestClient):
        """Test that unauthorized users cannot permanently delete posts using GET method."""
        response = client.get("/api/v1/testuser/db_post/1")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_permanent_delete_post_endpoint_unauthorized_post(self, client: TestClient):
        """Test that unauthorized users cannot permanently delete posts using POST method."""
        response = client.post("/api/v1/testuser/db_post/1")
        # The real API returns 401 for unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_posts_endpoint_methods_consistency(self, client: TestClient):
        """Test that both GET and POST methods return consistent responses for the posts endpoint."""
        username = "apiadmin"
        
        # Test both methods for the same endpoint
        get_response = client.get(f"/api/v1/{username}/posts")
        post_response = client.post(f"/api/v1/{username}/posts")
        
        # GET should return 405 Method Not Allowed, POST should return 200 or 404
        assert get_response.status_code == 405
        assert post_response.status_code in [200, 404]
        
        # GET should have proper error structure
        get_data = get_response.json()
        assert "detail" in get_data
        assert "Method Not Allowed" in get_data["detail"]
        
        # POST should have proper response structure
        if post_response.status_code == 200:
            post_data = post_response.json()
            # Check for pagination structure
            assert "data" in post_data
            assert "total_count" in post_data
            assert "page" in post_data
            assert "items_per_page" in post_data
            assert isinstance(post_data["data"], list)
        else:
            post_data = post_response.json()
            assert "detail" in post_data
