"""Integration tests for user CRUD operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from src.app.core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from src.app.crud.crud_users import crud_users
from src.app.models.user import User
from src.app.schemas.user import UserCreate, UserCreateInternal, UserUpdate
from src.app.core.security import get_password_hash


class TestWriteUser:
    """Test user creation operations."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, async_db: AsyncSession, sample_user_data):
        """Test successful user creation."""
        user_create = UserCreate(**sample_user_data)
        
        # Create user using CRUD directly
        user_internal_dict = user_create.model_dump()
        user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
        del user_internal_dict["password"]
        
        user_internal = UserCreateInternal(**user_internal_dict)
        created_user = await crud_users.create(db=async_db, object=user_internal)
        
        assert created_user is not None
        assert created_user.username == user_create.username
        assert created_user.email == user_create.email
        assert created_user.name == user_create.name
        assert created_user.id is not None

        # Verify user was actually created in database
        db_user = await crud_users.get(db=async_db, username=created_user.username)
        assert db_user is not None
        assert db_user["username"] == user_create.username
        assert db_user["email"] == user_create.email
        assert db_user["name"] == user_create.name

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, async_db: AsyncSession, sample_user_data):
        """Test user creation with duplicate email fails."""
        user_create = UserCreate(**sample_user_data)
        
        # Create first user
        user_internal_dict = user_create.model_dump()
        user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
        del user_internal_dict["password"]
        
        user_internal = UserCreateInternal(**user_internal_dict)
        await crud_users.create(db=async_db, object=user_internal)
        
        # Try to create second user with same email
        user_create2 = UserCreate(**sample_user_data)
        user_internal_dict2 = user_create2.model_dump()
        user_internal_dict2["hashed_password"] = get_password_hash(password=user_internal_dict2["password"])
        del user_internal_dict2["password"]
        
        user_internal2 = UserCreateInternal(**user_internal_dict2)
        
        # This should raise IntegrityError due to duplicate email constraint
        with pytest.raises(IntegrityError):
            await crud_users.create(db=async_db, object=user_internal2)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, async_db: AsyncSession, sample_user_data):
        """Test user creation with duplicate username fails."""
        user_create = UserCreate(**sample_user_data)
        
        # Create first user
        user_internal_dict = user_create.model_dump()
        user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
        del user_internal_dict["password"]
        
        user_internal = UserCreateInternal(**user_internal_dict)
        await crud_users.create(db=async_db, object=user_internal)
        
        # Try to create second user with same username but different email
        user_create2 = UserCreate(**sample_user_data)
        user_create2.email = "different@example.com"
        user_internal_dict2 = user_create2.model_dump()
        user_internal_dict2["hashed_password"] = get_password_hash(password=user_internal_dict2["password"])
        del user_internal_dict2["password"]
        
        user_internal2 = UserCreateInternal(**user_internal_dict2)
        
        # This should raise IntegrityError due to duplicate username constraint
        with pytest.raises(IntegrityError):
            await crud_users.create(db=async_db, object=user_internal2)


class TestReadUser:
    """Test user retrieval operations."""

    @pytest.mark.asyncio
    async def test_read_user_success(self, async_db: AsyncSession, sample_user_data):
        """Test successful user retrieval."""
        # Create a user first
        user_create = UserCreate(**sample_user_data)
        user_internal_dict = user_create.model_dump()
        user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
        del user_internal_dict["password"]
        
        user_internal = UserCreateInternal(**user_internal_dict)
        created_user = await crud_users.create(db=async_db, object=user_internal)
        
        # Read the user
        db_user = await crud_users.get(db=async_db, username=created_user.username, is_deleted=False)
        assert db_user is not None
        assert db_user["username"] == user_create.username
        assert db_user["email"] == user_create.email
        assert db_user["name"] == user_create.name

    @pytest.mark.asyncio
    async def test_read_user_not_found(self, async_db: AsyncSession):
        """Test user retrieval for non-existent user."""
        db_user = await crud_users.get(db=async_db, username="nonexistent", is_deleted=False)
        assert db_user is None


class TestUpdateUser:
    """Test user update operations."""

    @pytest.mark.asyncio
    async def test_patch_user_success(self, async_db: AsyncSession, sample_user_data):
        """Test successful user update."""
        # Create a user first
        user_create = UserCreate(**sample_user_data)
        user_internal_dict = user_create.model_dump()
        user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
        del user_internal_dict["password"]
        
        user_internal = UserCreateInternal(**user_internal_dict)
        created_user = await crud_users.create(db=async_db, object=user_internal)
        
        # Update the user
        user_update = UserUpdate(name="Updated Name")
        await crud_users.update(db=async_db, object=user_update, username=created_user.username)
        
        # Verify the update
        updated_user = await crud_users.get(db=async_db, username=created_user.username)
        assert updated_user is not None
        assert updated_user["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_patch_user_not_found(self, async_db: AsyncSession):
        """Test user update for non-existent user."""
        user_update = UserUpdate(name="Updated Name")
        # This should raise NoResultFound since no user exists with that username
        with pytest.raises(NoResultFound):
            await crud_users.update(db=async_db, object=user_update, username="nonexistent")


class TestDeleteUser:
    """Test user deletion operations."""

    @pytest.mark.asyncio
    async def test_erase_user_success(self, async_db: AsyncSession, sample_user_data):
        """Test successful user deletion."""
        # Create a user first
        user_create = UserCreate(**sample_user_data)
        user_internal_dict = user_create.model_dump()
        user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
        del user_internal_dict["password"]
        
        user_internal = UserCreateInternal(**user_internal_dict)
        created_user = await crud_users.create(db=async_db, object=user_internal)
        
        # Delete the user
        await crud_users.delete(db=async_db, username=created_user.username)
        
        # Verify soft deletion
        deleted_user = await crud_users.get(db=async_db, username=created_user.username)
        assert deleted_user is not None
        assert deleted_user["is_deleted"] is True
        assert deleted_user["deleted_at"] is not None

    @pytest.mark.asyncio
    async def test_erase_user_not_found(self, async_db: AsyncSession):
        """Test user deletion for non-existent user."""
        # This should raise NoResultFound since no user exists with that username
        with pytest.raises(NoResultFound):
            await crud_users.delete(db=async_db, username="nonexistent")
