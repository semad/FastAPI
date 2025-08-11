from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from src.app.core.config import settings
from src.app.main import app

DATABASE_URI = settings.POSTGRES_URI
DATABASE_PREFIX = settings.POSTGRES_SYNC_PREFIX

sync_engine = create_engine(DATABASE_PREFIX + DATABASE_URI)
local_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Create async engine for integration tests
async_engine = create_async_engine(
    f"postgresql+asyncpg://postgres:postgres@localhost:5432/sqlapi",
    echo=False,
)
async_session = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


fake = Faker()


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, Any, None]:
    with TestClient(app) as _client:
        yield _client
    app.dependency_overrides = {}
    sync_engine.dispose()


@pytest.fixture
def db() -> Generator[Session, Any, None]:
    session = local_session()
    yield session
    session.close()


@pytest_asyncio.fixture
async def async_db() -> AsyncSession:
    """Async database session for integration tests."""
    # Create a new engine for each test to avoid connection conflicts
    test_engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/sqlapi",
        echo=False,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )
    
    test_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    session = test_session()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
        await test_engine.dispose()


def override_dependency(dependency: Callable[..., Any], mocked_response: Any) -> None:
    app.dependency_overrides[dependency] = lambda: mocked_response


@pytest.fixture
def mock_db():
    """Mock database session for unit tests."""
    return Mock(spec=AsyncSession)


@pytest.fixture
def mock_redis():
    """Mock Redis connection for unit tests."""
    mock_redis = Mock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=True)
    return mock_redis


@pytest.fixture
def sample_user_data():
    """Generate sample user data for tests."""
    return {
        "name": fake.name(),
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
    }


@pytest.fixture
def sample_user_read():
    """Generate a sample UserRead object."""
    import uuid

    from src.app.schemas.user import UserRead

    return UserRead(
        id=1,
        uuid=uuid.uuid4(),
        name=fake.name(),
        username=fake.user_name(),
        email=fake.email(),
        profile_image_url=fake.image_url(),
        is_superuser=False,
        created_at=fake.date_time(),
        updated_at=fake.date_time(),
        tier_id=None,
    )


@pytest.fixture
def current_user_dict():
    """Mock current user from auth dependency."""
    return {
        "id": 1,
        "username": fake.user_name(),
        "email": fake.email(),
        "name": fake.name(),
        "is_superuser": False,
    }


def generate_valid_isbn():
    """Generate a valid ISBN that matches the pattern ^[0-9X-]{10,13}$"""
    # Generate a 13-digit ISBN without hyphens
    return fake.numerify(text="#############")


@pytest.fixture
def sample_book_data():
    """Generate sample book data for tests."""
    return {
        "title": fake.catch_phrase(),
        "author": fake.name(),
        "description": fake.text(max_nb_chars=500),
        "isbn": generate_valid_isbn(),
        "publication_year": fake.year(),
        "genre": fake.random_element(["Fiction", "Non-Fiction", "Science Fiction", "Mystery", "Romance"]),
        "pages": fake.random_int(min=50, max=1000),
        "cover_image_url": fake.image_url(),
    }


@pytest.fixture
def sample_book_read():
    """Generate a sample BookRead object."""
    import uuid

    from src.app.schemas.book import BookRead

    return BookRead(
        id=1,
        uuid=uuid.uuid4(),
        title=fake.catch_phrase(),
        author=fake.name(),
        description=fake.text(max_nb_chars=500),
        isbn=generate_valid_isbn(),
        publication_year=fake.year(),
        genre=fake.random_element(["Fiction", "Non-Fiction", "Science Fiction", "Mystery", "Romance"]),
        pages=fake.random_int(min=50, max=1000),
        cover_image_url=fake.image_url(),
        created_by_user_id=1,
        created_at=fake.date_time(),
        updated_at=fake.date_time(),
    )
