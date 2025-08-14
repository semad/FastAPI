"""Helper functions for API tests."""

from typing import Dict, Any
from faker import Faker

fake = Faker()

def generate_user_data() -> Dict[str, Any]:
    """Generate sample user data for API tests."""
    unique_suffix = fake.unique.random_number(digits=6)
    return {
        "name": fake.name(),
        "username": f"user{unique_suffix}",
        "email": f"user{unique_suffix}@example.com",
        "password": "testpassword123",
    }

def generate_book_data() -> dict:
    """Generate realistic book data for testing."""
    return {
        "title": fake.sentence(nb_words=3, variable_nb_words=True),
        "author": fake.name(),
        "description": fake.text(max_nb_chars=200),
        "isbn": fake.isbn13(),
        "price": round(fake.pyfloat(min_value=5.0, max_value=50.0), 2),
        "publication_date": fake.date_this_decade().isoformat(),
        "genre": fake.random_element(elements=["Fiction", "Non-Fiction", "Mystery", "Romance", "Sci-Fi"]),
        "page_count": fake.random_int(min=50, max=800),
        "language": fake.random_element(elements=["English", "Spanish", "French", "German"]),
        "publisher": fake.company(),
    }

def generate_post_data() -> Dict[str, Any]:
    """Generate sample post data for API tests."""
    unique_suffix = fake.unique.random_number(digits=6)
    return {
        "title": f"Test Post {unique_suffix}",
        "text": fake.text(max_nb_chars=500),
        "media_url": fake.image_url(),
    }

def generate_tier_data() -> Dict[str, Any]:
    """Generate sample tier data for API tests."""
    unique_suffix = fake.unique.random_number(digits=6)
    return {
        "name": f"Test Tier {unique_suffix}",
    }

def generate_rate_limit_data() -> Dict[str, Any]:
    """Generate sample rate limit data for API tests."""
    unique_suffix = fake.unique.random_number(digits=6)
    return {
        "name": f"Test Rate Limit {unique_suffix}",
        "path": f"/api/v1/test{unique_suffix}",
        "limit": fake.random_int(min=10, max=1000),
        "period": fake.random_int(min=60, max=86400),  # 1 minute to 1 day
    }

def assert_response_structure(response_data: Dict[str, Any], expected_keys: list) -> None:
    """Assert that response data has the expected structure."""
    for key in expected_keys:
        assert key in response_data, f"Expected key '{key}' not found in response"

def assert_pagination_structure(response_data: Dict[str, Any]) -> None:
    """Assert that response data has pagination structure."""
    expected_keys = ["data", "total_count", "page", "size", "pages"]
    assert_response_structure(response_data, expected_keys)
    assert isinstance(response_data["data"], list)
    assert isinstance(response_data["total_count"], int)
    assert response_data["total_count"] >= 0
