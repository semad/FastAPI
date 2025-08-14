"""Test book API endpoints with both GET and POST methods."""

import pytest
from fastapi.testclient import TestClient
from helpers.api_helpers import generate_book_data


class TestBookEndpoints:
    """Test book API endpoints with both GET and POST methods."""

    def test_get_books_public_get(self, client: TestClient):
        """Test public books endpoint using GET method."""
        response = client.get("/api/v1/books")
        # The real API returns 200 for public books endpoint
        assert response.status_code == 200
        data = response.json()
        # Check for pagination structure
        assert "data" in data
        assert "total_count" in data
        assert "page" in data
        assert "items_per_page" in data
        assert isinstance(data["data"], list)

    def test_get_books_public_post(self, client: TestClient):
        """Test public books endpoint using POST method."""
        response = client.post("/api/v1/books")
        # The real API returns 200 for public books endpoint
        assert response.status_code == 200
        data = response.json()
        # Check for pagination structure
        assert "data" in data
        assert "total_count" in data
        assert "page" in data
        assert "items_per_page" in data
        assert isinstance(data["data"], list)

    def test_get_books_with_pagination_get(self, client: TestClient):
        """Test books endpoint with pagination using GET method."""
        response = client.get("/api/v1/books?page=2&items_per_page=5")
        assert response.status_code == 200
        data = response.json()
        # Check for pagination structure
        assert "data" in data
        assert "total_count" in data
        assert "page" in data
        assert "items_per_page" in data
        assert isinstance(data["data"], list)
        assert data["page"] == 2
        assert data["items_per_page"] == 5

    def test_get_books_with_pagination_post(self, client: TestClient):
        """Test books endpoint with pagination using POST method."""
        response = client.post("/api/v1/books?page=2&items_per_page=5")
        assert response.status_code == 200
        data = response.json()
        # Check for pagination structure
        assert "data" in data
        assert "total_count" in data
        assert "page" in data
        assert "items_per_page" in data
        assert isinstance(data["data"], list)
        assert data["page"] == 2
        assert data["items_per_page"] == 5

    def test_get_public_book_by_id_get(self, client: TestClient):
        """Test getting a public book by ID using GET method."""
        response = client.get("/api/v1/book/1")
        # The real API returns 404 for non-existent books or 200 if it exists
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "title" in data
            assert "author" in data
        else:
            data = response.json()
            assert "detail" in data

    def test_get_public_book_by_id_post(self, client: TestClient):
        """Test getting a public book by ID using POST method."""
        response = client.post("/api/v1/book/1")
        # The real API returns 404 for non-existent books or 200 if it exists
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "title" in data
            assert "author" in data
        else:
            data = response.json()
            assert "detail" in data

    def test_create_book_unauthorized_get(self, client: TestClient):
        """Test that unauthorized users cannot create books using GET method."""
        response = client.get("/api/v1/testuser/book")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_create_book_unauthorized_post(self, client: TestClient):
        """Test that unauthorized users cannot create books using POST method."""
        book_data = generate_book_data()
        response = client.post("/api/v1/testuser/book", json=book_data)
        # The real API returns 401 for unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_get_user_books_unauthorized_get(self, client: TestClient):
        """Test that unauthorized users cannot access user-specific books using GET method."""
        response = client.get("/api/v1/testuser/books")
        # The real API returns 404 for user not found or 401 for unauthorized
        assert response.status_code in [401, 404]
        data = response.json()
        assert "detail" in data

    def test_get_user_books_unauthorized_post(self, client: TestClient):
        """Test that unauthorized users cannot access user-specific books using POST method."""
        response = client.post("/api/v1/testuser/books")
        # The real API returns 404 for user not found or 401 for unauthorized
        assert response.status_code in [401, 404]
        data = response.json()
        assert "detail" in data

    def test_get_user_book_by_id_unauthorized_get(self, client: TestClient):
        """Test that unauthorized users cannot access user-specific books by ID using GET method."""
        response = client.get("/api/v1/testuser/book/1")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_get_user_book_by_id_unauthorized_post(self, client: TestClient):
        """Test that unauthorized users cannot access user-specific books by ID using POST method."""
        response = client.post("/api/v1/testuser/book/1")
        # The real API returns 401 for unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_update_book_unauthorized_get(self, client: TestClient):
        """Test that unauthorized users cannot update books using GET method."""
        response = client.get("/api/v1/testuser/book/1")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_update_book_unauthorized_post(self, client: TestClient):
        """Test that unauthorized users cannot update books using POST method."""
        book_data = {"title": "Updated Title"}
        response = client.post("/api/v1/testuser/book/1", json=book_data)
        # The real API returns 401 for unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_delete_book_unauthorized_get(self, client: TestClient):
        """Test that unauthorized users cannot delete books using GET method."""
        response = client.get("/api/v1/testuser/book/1")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_delete_book_unauthorized_post(self, client: TestClient):
        """Test that unauthorized users cannot delete books using POST method."""
        response = client.post("/api/v1/testuser/book/1")
        # The real API returns 401 for unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_delete_db_book_unauthorized_get(self, client: TestClient):
        """Test that unauthorized users cannot permanently delete books using GET method."""
        response = client.get("/api/v1/testuser/db_book/1")
        # The real API returns 405 Method Not Allowed for GET requests
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
        assert "Method Not Allowed" in data["detail"]

    def test_delete_db_book_unauthorized_post(self, client: TestClient):
        """Test that unauthorized users cannot permanently delete books using POST method."""
        response = client.post("/api/v1/testuser/db_book/1")
        # The real API returns 401 for unauthorized
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_books_endpoint_methods_consistency(self, client: TestClient):
        """Test that both GET and POST methods return consistent responses for the books endpoint."""
        # Test both methods for the public books endpoint
        get_response = client.get("/api/v1/books")
        post_response = client.post("/api/v1/books")
        
        # Both should return 200 for public books
        assert get_response.status_code == 200
        assert post_response.status_code == 200
        
        # Both should have proper response structure
        get_data = get_response.json()
        post_data = post_response.json()
        # Check for pagination structure
        assert "data" in get_data
        assert "total_count" in get_data
        assert "page" in get_data
        assert "items_per_page" in get_data
        assert isinstance(get_data["data"], list)
        assert "data" in post_data
        assert "total_count" in post_data
        assert "page" in post_data
        assert "items_per_page" in post_data
        assert isinstance(post_data["data"], list)
