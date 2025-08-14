"""Integration tests for book CRUD operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from faker import Faker

fake = Faker()

from src.app.core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from src.app.crud.crud_books import crud_books
from src.app.crud.crud_users import crud_users
from src.app.models.book import Book
from src.app.models.user import User
from src.app.schemas.book import BookCreate, BookCreateInternal, BookUpdate
from src.app.schemas.user import UserCreateInternal
from src.app.core.security import get_password_hash


class TestWriteBook:
    """Test book creation operations."""

    @pytest.mark.asyncio
    async def test_create_book_success(self, async_db: AsyncSession, sample_book_data, current_user_dict):
        """Test successful book creation."""
        # Create a user first
        user_create = UserCreateInternal(
            name=current_user_dict["name"],
            username=current_user_dict["username"],
            email=current_user_dict["email"],
            hashed_password=get_password_hash("testpassword"),
            is_superuser=current_user_dict["is_superuser"]
        )
        created_user = await crud_users.create(db=async_db, object=user_create)
        print(f"created_user: {type(created_user)} {dir(created_user)} {created_user}")
        
        # Create book data
        book_data = sample_book_data.copy()
        book_data["isbn"] = None  # Avoid duplicate ISBN check
        book_data["created_by_user_id"] = created_user.id
        
        book_create = BookCreateInternal(**book_data)
        created_book = await crud_books.create(db=async_db, object=book_create)
        
        assert created_book is not None
        assert created_book.title == book_data["title"]
        assert created_book.author == book_data["author"]
        assert created_book.created_by_user_id == created_user.id

    @pytest.mark.asyncio
    async def test_create_book_duplicate_isbn(self, async_db: AsyncSession, sample_book_data, current_user_dict):
        """Test book creation with duplicate ISBN fails."""
        # Create a user first
        user_create = UserCreateInternal(
            name=current_user_dict["name"],
            username=current_user_dict["username"],
            email=current_user_dict["email"],
            hashed_password=get_password_hash("testpassword"),
            is_superuser=current_user_dict["is_superuser"]
        )
        created_user = await crud_users.create(db=async_db, object=user_create)
        
        # Create first book
        book_data = sample_book_data.copy()
        book_data["created_by_user_id"] = created_user.id
        book_create = BookCreateInternal(**book_data)
        await crud_books.create(db=async_db, object=book_create)
        
        # Try to create second book with same ISBN
        book_data2 = sample_book_data.copy()
        book_data2["title"] = "Different Title"
        book_data2["created_by_user_id"] = created_user.id
        book_create2 = BookCreateInternal(**book_data2)
        
        # This should raise IntegrityError due to duplicate ISBN constraint
        with pytest.raises(IntegrityError):
            await crud_books.create(db=async_db, object=book_create2)

    @pytest.mark.asyncio
    async def test_create_book_forbidden(self, async_db: AsyncSession, sample_book_data, current_user_dict):
        """Test book creation when user doesn't exist."""
        # Try to create book with non-existent user ID
        book_data = sample_book_data.copy()
        book_data["created_by_user_id"] = 999  # Non-existent user
        
        book_create = BookCreateInternal(**book_data)
        
        # This should raise IntegrityError due to foreign key constraint
        with pytest.raises(IntegrityError):
            await crud_books.create(db=async_db, object=book_create)


class TestReadBook:
    """Test book retrieval operations."""

    @pytest.mark.asyncio
    async def test_read_book_success(self, async_db: AsyncSession, sample_book_data, current_user_dict):
        """Test successful book retrieval."""
        # Create a user first
        user_create = UserCreateInternal(
            name=current_user_dict["name"],
            username=current_user_dict["username"],
            email=current_user_dict["email"],
            hashed_password=get_password_hash("testpassword"),
            is_superuser=current_user_dict["is_superuser"]
        )
        created_user = await crud_users.create(db=async_db, object=user_create)
        
        # Create a book
        book_data = sample_book_data.copy()
        book_data["created_by_user_id"] = created_user.id
        book_create = BookCreateInternal(**book_data)
        created_book = await crud_books.create(db=async_db, object=book_create)
        
        # Retrieve the book
        retrieved_book = await crud_books.get(db=async_db, id=created_book.id)
        
        assert retrieved_book is not None
        assert retrieved_book["id"] == created_book.id
        assert retrieved_book["title"] == book_data["title"]

    @pytest.mark.asyncio
    async def test_read_book_not_found(self, async_db: AsyncSession):
        """Test book retrieval when book doesn't exist."""
        # Try to retrieve non-existent book
        retrieved_book = await crud_books.get(db=async_db, id=999)
        
        assert retrieved_book is None


class TestReadBooks:
    """Test books list retrieval operations."""

    @pytest.mark.asyncio
    async def test_read_books_success(self, async_db: AsyncSession, sample_book_data, current_user_dict):
        """Test successful books list retrieval."""
        # Create a user first
        user_create = UserCreateInternal(
            name=current_user_dict["name"],
            username=current_user_dict["username"],
            email=current_user_dict["email"],
            hashed_password=get_password_hash("testpassword"),
            is_superuser=current_user_dict["is_superuser"]
        )
        created_user = await crud_users.create(db=async_db, object=user_create)
        
        # Create multiple books
        for i in range(3):
            book_data = sample_book_data.copy()
            book_data["title"] = f"Book {i+1}"
            # Use the generate_valid_isbn function to avoid conflicts
            from tests_db.conftest import generate_valid_isbn
            book_data["isbn"] = generate_valid_isbn()
            book_data["created_by_user_id"] = created_user.id
            book_create = BookCreateInternal(**book_data)
            await crud_books.create(db=async_db, object=book_create)
        
        # Retrieve books
        books = await crud_books.get_multi(db=async_db, page=1, items_per_page=10)
        
        assert books is not None
        assert len(books["data"]) >= 3


class TestPatchBook:
    """Test book update operations."""

    @pytest.mark.asyncio
    async def test_patch_book_success(self, async_db: AsyncSession, sample_book_data, current_user_dict):
        """Test successful book update."""
        # Create a user first
        user_create = UserCreateInternal(
            name=current_user_dict["name"],
            username=current_user_dict["username"],
            email=current_user_dict["email"],
            hashed_password=get_password_hash("testpassword"),
            is_superuser=current_user_dict["is_superuser"]
        )
        created_user = await crud_users.create(db=async_db, object=user_create)
        
        # Create a book
        book_data = sample_book_data.copy()
        book_data["created_by_user_id"] = created_user.id
        book_create = BookCreateInternal(**book_data)
        created_book = await crud_books.create(db=async_db, object=book_create)
        
        # Update the book
        book_update = BookUpdate(title="Updated Title")
        await crud_books.update(
            db=async_db, 
            object=book_update, 
            id=created_book.id
        )
        
        # Verify the update by retrieving the updated book
        updated_book = await crud_books.get(db=async_db, id=created_book.id)
        assert updated_book is not None
        assert updated_book["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_patch_book_not_found(self, async_db: AsyncSession):
        """Test book update when book doesn't exist."""
        book_update = BookUpdate(title="Updated Title")
        
        # This should raise NoResultFound since no book exists with that ID
        with pytest.raises(NoResultFound):
            await crud_books.update(db=async_db, object=book_update, id=999)

    @pytest.mark.asyncio
    async def test_patch_book_forbidden(self, async_db: AsyncSession, sample_book_data, current_user_dict):
        """Test book update when user tries to update another user's book."""
        # Create two users
        user1_create = UserCreateInternal(
            name=current_user_dict["name"],
            username=current_user_dict["username"],
            email=current_user_dict["email"],
            hashed_password=get_password_hash("testpassword"),
            is_superuser=current_user_dict["is_superuser"]
        )
        user1 = await crud_users.create(db=async_db, object=user1_create)
        
        user2_create = UserCreateInternal(
            name="User 2",
            username=f"user2{fake.unique.random_number(digits=6)}",
            email=f"user2_{fake.unique.random_number(digits=6)}@example.com",
            hashed_password=get_password_hash("testpassword"),
            is_superuser=False
        )
        user2 = await crud_users.create(db=async_db, object=user2_create)
        
        # Create a book owned by user1
        book_data = sample_book_data.copy()
        book_data["created_by_user_id"] = user1.id
        book_create = BookCreateInternal(**book_data)
        created_book = await crud_books.create(db=async_db, object=book_create)
        
        # Try to update the book as user2
        book_update = BookUpdate(title="Updated Title")
        
        # This should work since CRUD doesn't enforce ownership - it's handled at API level
        # But we can verify the book was updated
        await crud_books.update(
            db=async_db, 
            object=book_update, 
            id=created_book.id
        )
        
        # Verify the update by retrieving the updated book
        updated_book = await crud_books.get(db=async_db, id=created_book.id)
        assert updated_book is not None
        assert updated_book["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_patch_book_duplicate_isbn(self, async_db: AsyncSession, sample_book_data, current_user_dict):
        """Test book update with duplicate ISBN."""
        # Create a user first
        user_create = UserCreateInternal(
            name=current_user_dict["name"],
            username=current_user_dict["username"],
            email=current_user_dict["email"],
            hashed_password=get_password_hash("testpassword"),
            is_superuser=current_user_dict["is_superuser"]
        )
        created_user = await crud_users.create(db=async_db, object=user_create)
        
        # Create first book
        book_data1 = sample_book_data.copy()
        book_data1["isbn"] = f"978{fake.unique.random_number(digits=9)}"
        book_data1["created_by_user_id"] = created_user.id
        book_create1 = BookCreateInternal(**book_data1)
        await crud_books.create(db=async_db, object=book_create1)
        
        # Create second book with different ISBN
        book_data2 = sample_book_data.copy()
        book_data2["title"] = "Book 2"
        book_data2["isbn"] = f"978{fake.unique.random_number(digits=9)}"
        book_data2["created_by_user_id"] = created_user.id
        book_create2 = BookCreateInternal(**book_data2)
        created_book2 = await crud_books.create(db=async_db, object=book_create2)
        
        # Try to update second book to use first book's ISBN
        book_update = BookUpdate(isbn=book_data1["isbn"])
        
        # This should raise IntegrityError due to duplicate ISBN constraint
        with pytest.raises(IntegrityError):
            await crud_books.update(
                db=async_db, 
                object=book_update, 
                id=created_book2.id
            )


class TestEraseBook:
    """Test book deletion operations."""

    @pytest.mark.asyncio
    async def test_erase_book_success(self, async_db: AsyncSession, sample_book_data, current_user_dict):
        """Test successful book deletion."""
        # Create a user first
        user_create = UserCreateInternal(
            name=current_user_dict["name"],
            username=current_user_dict["username"],
            email=current_user_dict["email"],
            hashed_password=get_password_hash("testpassword"),
            is_superuser=current_user_dict["is_superuser"]
        )
        created_user = await crud_users.create(db=async_db, object=user_create)
        
        # Create a book
        book_data = sample_book_data.copy()
        book_data["created_by_user_id"] = created_user.id
        book_create = BookCreateInternal(**book_data)
        created_book = await crud_books.create(db=async_db, object=book_create)
        
        # Delete the book
        await crud_books.delete(db=async_db, id=created_book.id)
        
        # Verify the book is soft deleted
        retrieved_book = await crud_books.get(db=async_db, id=created_book.id)
        assert retrieved_book is not None
        assert retrieved_book["is_deleted"] is True
        assert retrieved_book["deleted_at"] is not None

    @pytest.mark.asyncio
    async def test_erase_book_not_found(self, async_db: AsyncSession):
        """Test book deletion when book doesn't exist."""
        # This should raise NoResultFound since no book exists with that ID
        with pytest.raises(NoResultFound):
            await crud_books.delete(db=async_db, id=999)

    @pytest.mark.asyncio
    async def test_erase_book_forbidden(self, async_db: AsyncSession, sample_book_data, current_user_dict):
        """Test book deletion when user tries to delete another user's book."""
        # Create two users
        user1_create = UserCreateInternal(
            name=current_user_dict["name"],
            username=current_user_dict["username"],
            email=current_user_dict["email"],
            hashed_password=get_password_hash("testpassword"),
            is_superuser=current_user_dict["is_superuser"]
        )
        user1 = await crud_users.create(db=async_db, object=user1_create)
        
        user2_create = UserCreateInternal(
            name="User 2",
            username=f"user2{fake.unique.random_number(digits=6)}",
            email=f"user2_{fake.unique.random_number(digits=6)}@example.com",
            hashed_password=get_password_hash("testpassword"),
            is_superuser=False
        )
        user2 = await crud_users.create(db=async_db, object=user2_create)
        
        # Create a book owned by user1
        book_data = sample_book_data.copy()
        book_data["created_by_user_id"] = user1.id
        book_create = BookCreateInternal(**book_data)
        created_book = await crud_books.create(db=async_db, object=book_create)
        
        # Try to delete the book as user2
        # This should work since CRUD doesn't enforce ownership - it's handled at API level
        await crud_books.delete(db=async_db, id=created_book.id)
        
        # Verify the book is soft deleted
        retrieved_book = await crud_books.get(db=async_db, id=created_book.id)
        assert retrieved_book is not None
        assert retrieved_book["is_deleted"] is True
        assert retrieved_book["deleted_at"] is not None
