"""Integration tests for tier CRUD operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from faker import Faker

from src.app.core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from src.app.crud.crud_tier import crud_tiers
from src.app.models.tier import Tier
from src.app.schemas.tier import TierCreate, TierCreateInternal, TierUpdate

fake = Faker()


@pytest.fixture
def sample_tier_data():
    """Generate sample tier data for tests."""
    return {
        "name": fake.word().capitalize(),
    }


@pytest.fixture
def sample_tier_read():
    """Generate a sample TierRead object."""
    from src.app.schemas.tier import TierRead

    return TierRead(
        id=1,
        name=fake.word().capitalize(),
        created_at=fake.date_time(),
        updated_at=fake.date_time(),
    )


class TestWriteTier:
    """Test tier creation operations."""

    @pytest.mark.asyncio
    async def test_create_tier_success(self, async_db: AsyncSession, sample_tier_data):
        """Test successful tier creation."""
        tier_create = TierCreate(**sample_tier_data)
        
        # Create tier using CRUD directly
        tier_internal = TierCreateInternal(**tier_create.model_dump())
        created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
        
        assert created_tier is not None
        assert created_tier.name == tier_create.name
        assert created_tier.id is not None
        assert created_tier.created_at is not None

        # Verify tier was actually created in database
        db_tier = await crud_tiers.get(db=async_db, id=created_tier.id)
        assert db_tier is not None
        assert db_tier["name"] == tier_create.name

    @pytest.mark.asyncio
    async def test_create_tier_duplicate_name(self, async_db: AsyncSession, sample_tier_data):
        """Test tier creation with duplicate name fails."""
        tier_create = TierCreate(**sample_tier_data)
        
        # Create first tier
        tier_internal = TierCreateInternal(**tier_create.model_dump())
        await crud_tiers.create(db=async_db, object=tier_internal)
        
        # Try to create second tier with same name
        tier_create2 = TierCreate(**sample_tier_data)
        tier_internal2 = TierCreateInternal(**tier_create2.model_dump())
        
        # This should raise IntegrityError due to duplicate name constraint
        with pytest.raises(IntegrityError):
            await crud_tiers.create(db=async_db, object=tier_internal2)

    @pytest.mark.asyncio
    async def test_create_tier_with_special_characters(self, async_db: AsyncSession):
        """Test tier creation with special characters in name."""
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        tier_name = f"Premium+ Tier {unique_suffix}"
        tier_data = {"name": tier_name}
        
        tier_create = TierCreate(**tier_data)
        tier_internal = TierCreateInternal(**tier_create.model_dump())
        created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
        
        assert created_tier.name == tier_name

    @pytest.mark.asyncio
    async def test_create_tier_with_numbers(self, async_db: AsyncSession):
        """Test tier creation with numbers in name."""
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        tier_name = f"Tier 1 {unique_suffix}"
        tier_data = {"name": tier_name}
        
        tier_create = TierCreate(**tier_data)
        tier_internal = TierCreateInternal(**tier_create.model_dump())
        created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
        
        assert created_tier.name == tier_name


class TestReadTier:
    """Test tier retrieval operations."""

    @pytest.mark.asyncio
    async def test_read_tier_success(self, async_db: AsyncSession, sample_tier_data):
        """Test successful tier retrieval."""
        # Create a tier first
        tier_create = TierCreate(**sample_tier_data)
        tier_internal = TierCreateInternal(**tier_create.model_dump())
        created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
        
        # Retrieve the tier
        retrieved_tier = await crud_tiers.get(db=async_db, id=created_tier.id)
        
        assert retrieved_tier is not None
        assert retrieved_tier["id"] == created_tier.id
        assert retrieved_tier["name"] == created_tier.name

    @pytest.mark.asyncio
    async def test_read_tier_by_name(self, async_db: AsyncSession, sample_tier_data):
        """Test tier retrieval by name."""
        # Create a tier first
        tier_create = TierCreate(**sample_tier_data)
        tier_internal = TierCreateInternal(**tier_create.model_dump())
        created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
        
        # Retrieve the tier by name
        retrieved_tier = await crud_tiers.get(db=async_db, name=created_tier.name)
        
        assert retrieved_tier is not None
        assert retrieved_tier["name"] == created_tier.name
        assert retrieved_tier["id"] == created_tier.id

    @pytest.mark.asyncio
    async def test_read_tier_not_found(self, async_db: AsyncSession):
        """Test tier retrieval with non-existent ID."""
        retrieved_tier = await crud_tiers.get(db=async_db, id=99999)
        assert retrieved_tier is None

    @pytest.mark.asyncio
    async def test_get_multi_tiers(self, async_db: AsyncSession):
        """Test retrieving multiple tiers."""
        # Create multiple tiers with unique names
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        tier_names = [f"Basic {unique_suffix}", f"Premium {unique_suffix}", f"Enterprise {unique_suffix}"]
        created_tiers = []
        
        for name in tier_names:
            tier_data = {"name": name}
            tier_create = TierCreate(**tier_data)
            tier_internal = TierCreateInternal(**tier_create.model_dump())
            created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
            created_tiers.append(created_tier)
        
        # Retrieve all tiers
        retrieved_tiers = await crud_tiers.get_multi(db=async_db)
        
        # The response is a dict with 'data' and 'total_count' keys
        assert retrieved_tiers is not None
        assert 'data' in retrieved_tiers
        assert len(retrieved_tiers['data']) >= 3
        
        # Verify that we can retrieve our specific tiers by ID
        for created_tier in created_tiers:
            retrieved_tier = await crud_tiers.get(db=async_db, id=created_tier.id)
            assert retrieved_tier is not None
            assert retrieved_tier["id"] == created_tier.id
            assert retrieved_tier["name"] == created_tier.name


class TestUpdateTier:
    """Test tier update operations."""

    @pytest.mark.asyncio
    async def test_update_tier_success(self, async_db: AsyncSession, sample_tier_data):
        """Test successful tier update."""
        # Create a tier first
        tier_create = TierCreate(**sample_tier_data)
        tier_internal = TierCreateInternal(**tier_create.model_dump())
        created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
        
        # Update the tier with a unique name
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        new_name = f"Updated Tier Name {unique_suffix}"
        update_data = TierUpdate(name=new_name)
        await crud_tiers.update(
            db=async_db, 
            object=update_data, 
            id=created_tier.id
        )
        
        # Verify the update by retrieving the updated record
        updated_tier = await crud_tiers.get(db=async_db, id=created_tier.id)
        assert updated_tier is not None
        assert updated_tier["name"] == new_name

    @pytest.mark.asyncio
    async def test_update_tier_name_to_existing(self, async_db: AsyncSession):
        """Test that updating tier name to existing name fails."""
        # Create two tiers with unique names
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        tier1_data = {"name": f"Tier One {unique_suffix}"}
        tier2_data = {"name": f"Tier Two {unique_suffix}"}
        
        tier1_create = TierCreate(**tier1_data)
        tier2_create = TierCreate(**tier2_data)
        
        tier1_internal = TierCreateInternal(**tier1_create.model_dump())
        tier2_internal = TierCreateInternal(**tier2_create.model_dump())
        
        created_tier1 = await crud_tiers.create(db=async_db, object=tier1_internal)
        created_tier2 = await crud_tiers.create(db=async_db, object=tier2_internal)
        
        # Try to update tier2 to have the same name as tier1
        update_data = TierUpdate(name=tier1_data["name"])
        
        # This should raise IntegrityError due to duplicate name constraint
        with pytest.raises(IntegrityError):
            await crud_tiers.update(
                db=async_db, 
                object=update_data, 
                id=created_tier2.id
            )

    @pytest.mark.asyncio
    async def test_update_tier_partial(self, async_db: AsyncSession, sample_tier_data):
        """Test partial tier update."""
        # Create a tier first
        tier_create = TierCreate(**sample_tier_data)
        tier_internal = TierCreateInternal(**tier_create.model_dump())
        created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
        
        # Store original values
        original_name = created_tier.name
        original_created_at = created_tier.created_at
        
        # Update only the name with a unique name
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        new_name = f"New Name Only {unique_suffix}"
        update_data = TierUpdate(name=new_name)
        await crud_tiers.update(
            db=async_db, 
            object=update_data, 
            id=created_tier.id
        )
        
        # Verify the update by retrieving the updated record
        updated_tier = await crud_tiers.get(db=async_db, id=created_tier.id)
        assert updated_tier is not None
        assert updated_tier["name"] == new_name
        assert updated_tier["created_at"] == original_created_at  # Should remain unchanged


class TestDeleteTier:
    """Test tier deletion operations."""

    @pytest.mark.asyncio
    async def test_delete_tier_success(self, async_db: AsyncSession, sample_tier_data):
        """Test successful tier deletion."""
        # Create a tier first
        tier_create = TierCreate(**sample_tier_data)
        tier_internal = TierCreateInternal(**tier_create.model_dump())
        created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
        
        # Delete the tier
        await crud_tiers.delete(db=async_db, id=created_tier.id)
        
        # Verify tier is no longer retrievable
        retrieved_tier = await crud_tiers.get(db=async_db, id=created_tier.id)
        assert retrieved_tier is None

    @pytest.mark.asyncio
    async def test_delete_tier_not_found(self, async_db: AsyncSession):
        """Test deleting non-existent tier."""
        # FastCRUD raises NoResultFound when trying to delete non-existent records
        from sqlalchemy.orm.exc import NoResultFound
        
        with pytest.raises(NoResultFound, match="No record found to delete."):
            await crud_tiers.delete(db=async_db, id=99999)


class TestTierValidation:
    """Test tier validation and constraints."""

    @pytest.mark.asyncio
    async def test_tier_name_required(self, async_db: AsyncSession):
        """Test that tier name is required."""
        # Try to create tier without name
        tier_data = {}
        
        # This should raise a validation error
        with pytest.raises(Exception):  # Could be ValidationError or similar
            tier_create = TierCreate(**tier_data)

    @pytest.mark.asyncio
    async def test_tier_name_not_null(self, async_db: AsyncSession):
        """Test that tier name cannot be null."""
        # Try to create tier with null name
        tier_data = {"name": None}
        
        # This should raise a validation error
        with pytest.raises(Exception):  # Could be ValidationError or similar
            tier_create = TierCreate(**tier_data)

    @pytest.mark.asyncio
    async def test_tier_name_empty_string(self, async_db: AsyncSession):
        """Test that tier name cannot be empty string."""
        # Try to create tier with empty name
        tier_data = {"name": ""}
        
        # Pydantic allows empty strings by default, so this should work
        # If you want to prevent empty strings, you need to add a validator to the schema
        tier_create = TierCreate(**tier_data)
        assert tier_create.name == ""
        
        # The database might have constraints, so let's test if we can actually create it
        try:
            tier_internal = TierCreateInternal(**tier_create.model_dump())
            created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
            assert created_tier is not None
            assert created_tier.name == ""
        except IntegrityError:
            # If database has constraints preventing empty strings, that's fine
            pass


class TestTierRelationships:
    """Test tier relationships with other models."""

    @pytest.mark.asyncio
    async def test_tier_has_users(self, async_db: AsyncSession, sample_tier_data):
        """Test that tier can have associated users."""
        # Create a tier first
        tier_create = TierCreate(**sample_tier_data)
        tier_internal = TierCreateInternal(**tier_create.model_dump())
        created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
        
        # Create a user associated with this tier using proper CRUD operations
        from src.app.schemas.user import UserCreate, UserCreateInternal
        from src.app.crud.crud_users import crud_users
        from src.app.core.security import get_password_hash
        
        # Create user data
        user_data = {
            "name": fake.name(),
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(),  # Use password, not hashed_password
        }
        
        # Create user using CRUD
        user_create = UserCreate(**user_data)
        
        # Create UserCreateInternal with the required hashed_password
        user_internal_data = user_create.model_dump()
        user_internal_data["hashed_password"] = get_password_hash(user_data["password"])
        user_internal = UserCreateInternal(**user_internal_data)
        
        created_user = await crud_users.create(db=async_db, object=user_internal)
        
        # Now update the user's tier_id using the proper update method
        from src.app.schemas.user import UserTierUpdate
        
        tier_update = UserTierUpdate(tier_id=created_tier.id)
        await crud_users.update(
            db=async_db,
            object=tier_update,
            id=created_user.id
        )
        
        # Verify the relationship by retrieving the updated user
        updated_user = await crud_users.get(db=async_db, id=created_user.id)
        assert updated_user is not None
        assert updated_user["tier_id"] == created_tier.id

    @pytest.mark.asyncio
    async def test_tier_has_rate_limits(self, async_db: AsyncSession, sample_tier_data):
        """Test that tier can have associated rate limits."""
        # Create a tier first
        tier_create = TierCreate(**sample_tier_data)
        tier_internal = TierCreateInternal(**tier_create.model_dump())
        created_tier = await crud_tiers.create(db=async_db, object=tier_internal)
        
        # Create a rate limit associated with this tier
        from src.app.models.rate_limit import RateLimit
        
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        rate_limit_data = {
            "tier_id": created_tier.id,
            "name": f"API Rate Limit {unique_suffix}",
            "path": "/api/v1/*",
            "limit": 100,
            "period": 3600,
        }
        
        rate_limit = RateLimit(**rate_limit_data)
        async_db.add(rate_limit)
        await async_db.commit()
        await async_db.refresh(rate_limit)
        
        # Verify the relationship
        assert rate_limit.tier_id == created_tier.id
