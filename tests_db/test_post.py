"""Integration tests for post CRUD operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from faker import Faker

from src.app.core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from src.app.crud.crud_posts import crud_posts
from src.app.models.post import Post
from src.app.models.user import User
from src.app.schemas.post import PostCreate, PostCreateInternal, PostUpdate
from src.app.core.security import get_password_hash

fake = Faker()


@pytest.fixture
def sample_post_data():
    """Generate sample post data for tests."""
    import uuid
    
    unique_suffix = str(uuid.uuid4())[:8]
    # Ensure title is within 30 character limit
    title = fake.word().capitalize()[:20] + f"_{unique_suffix}"
    
    return {
        "title": title,
        "text": fake.text(max_nb_chars=1000),
        "media_url": fake.image_url(),
    }


@pytest.fixture
def sample_post_read():
    """Generate a sample PostRead object."""
    import uuid
    from src.app.schemas.post import PostRead

    return PostRead(
        id=1,
        uuid=uuid.uuid4(),
        title=fake.catch_phrase(),
        text=fake.text(max_nb_chars=1000),
        media_url=fake.image_url(),
        created_by_user_id=1,
        created_at=fake.date_time(),
        updated_at=fake.date_time(),
    )


@pytest.fixture
async def sample_user(async_db: AsyncSession):
    """Create a sample user for testing posts."""
    import uuid
    
    unique_suffix = str(uuid.uuid4())[:4]  # Use shorter suffix
    # Ensure username stays within 20 character limit
    base_username = fake.user_name()[:15]  # Limit base username to 15 chars
    username = f"{base_username}_{unique_suffix}"  # Total: 15 + 1 + 4 = 20 chars
    
    user_data = {
        "name": fake.name(),
        "username": username,
        "email": fake.email(),
        "hashed_password": get_password_hash(fake.password()),
        "profile_image_url": fake.image_url(),
        "is_superuser": False,
    }
    
    user = User(**user_data)
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)
    
    return user


class TestWritePost:
    """Test post creation operations."""

    @pytest.mark.asyncio
    async def test_create_post_success(self, async_db: AsyncSession, sample_post_data, sample_user):
        """Test successful post creation."""
        post_create = PostCreate(**sample_post_data)
        
        # Create post using CRUD directly
        post_internal_dict = post_create.model_dump()
        post_internal_dict["created_by_user_id"] = sample_user.id
        
        post_internal = PostCreateInternal(**post_internal_dict)
        created_post = await crud_posts.create(db=async_db, object=post_internal)
        
        assert created_post is not None
        assert created_post.title == post_create.title
        assert created_post.text == post_create.text
        assert created_post.media_url == post_create.media_url
        assert created_post.created_by_user_id == sample_user.id
        assert created_post.id is not None

        # Verify post was actually created in database
        db_post = await crud_posts.get(db=async_db, id=created_post.id)
        assert db_post is not None
        assert db_post["title"] == post_create.title
        assert db_post["text"] == post_create.text
        assert db_post["media_url"] == post_create.media_url

    @pytest.mark.asyncio
    async def test_create_post_without_media(self, async_db: AsyncSession, sample_post_data, sample_user):
        """Test post creation without media URL."""
        post_data = sample_post_data.copy()
        post_data["media_url"] = None
        
        post_create = PostCreate(**post_data)
        post_internal_dict = post_create.model_dump()
        post_internal_dict["created_by_user_id"] = sample_user.id
        
        post_internal = PostCreateInternal(**post_internal_dict)
        created_post = await crud_posts.create(db=async_db, object=post_internal)
        
        assert created_post.media_url is None
        assert created_post.title == post_create.title
        assert created_post.text == post_create.text

    @pytest.mark.asyncio
    async def test_create_post_minimal_data(self, async_db: AsyncSession, sample_user):
        """Test post creation with minimal required data."""
        post_data = {
            "title": "Test Post",
            "text": "Test content",
        }
        
        post_create = PostCreate(**post_data)
        post_internal_dict = post_create.model_dump()
        post_internal_dict["created_by_user_id"] = sample_user.id
        
        post_internal = PostCreateInternal(**post_internal_dict)
        created_post = await crud_posts.create(db=async_db, object=post_internal)
        
        assert created_post.title == "Test Post"
        assert created_post.text == "Test content"
        assert created_post.media_url is None


class TestReadPost:
    """Test post retrieval operations."""

    @pytest.mark.asyncio
    async def test_read_post_success(self, async_db: AsyncSession, sample_post_data, sample_user):
        """Test successful post retrieval."""
        # Create a post first
        post_create = PostCreate(**sample_post_data)
        post_internal_dict = post_create.model_dump()
        post_internal_dict["created_by_user_id"] = sample_user.id
        
        post_internal = PostCreateInternal(**post_internal_dict)
        created_post = await crud_posts.create(db=async_db, object=post_internal)
        
        # Retrieve the post
        retrieved_post = await crud_posts.get(db=async_db, id=created_post.id)
        
        assert retrieved_post is not None
        assert retrieved_post["id"] == created_post.id
        assert retrieved_post["title"] == created_post.title
        assert retrieved_post["text"] == created_post.text

    @pytest.mark.asyncio
    async def test_read_post_by_uuid(self, async_db: AsyncSession, sample_post_data, sample_user):
        """Test post retrieval by UUID."""
        # Create a post first
        post_create = PostCreate(**sample_post_data)
        post_internal_dict = post_create.model_dump()
        post_internal_dict["created_by_user_id"] = sample_user.id
        
        post_internal = PostCreateInternal(**post_internal_dict)
        created_post = await crud_posts.create(db=async_db, object=post_internal)
        
        # Retrieve the post by UUID
        retrieved_post = await crud_posts.get(db=async_db, uuid=created_post.uuid)
        
        assert retrieved_post is not None
        assert retrieved_post["uuid"] == created_post.uuid
        assert retrieved_post["title"] == created_post.title

    @pytest.mark.asyncio
    async def test_read_post_not_found(self, async_db: AsyncSession):
        """Test post retrieval with non-existent ID."""
        retrieved_post = await crud_posts.get(db=async_db, id=99999)
        assert retrieved_post is None

    @pytest.mark.asyncio
    async def test_get_multi_posts(self, async_db: AsyncSession, sample_user):
        """Test retrieving multiple posts."""
        # Create multiple posts with unique names
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        post_data_list = [
            {"title": f"Post {i}_{unique_suffix}", "text": f"Content {i}"} 
            for i in range(3)
        ]
        
        created_posts = []
        for post_data in post_data_list:
            post_create = PostCreate(**post_data)
            post_internal_dict = post_create.model_dump()
            post_internal_dict["created_by_user_id"] = sample_user.id
            
            post_internal = PostCreateInternal(**post_internal_dict)
            created_post = await crud_posts.create(db=async_db, object=post_internal)
            created_posts.append(created_post)
        
        # Retrieve all posts
        retrieved_posts = await crud_posts.get_multi(db=async_db)
        
        # get_multi returns a paginated result with 'data' key
        assert "data" in retrieved_posts
        assert len(retrieved_posts["data"]) >= 3
        # Check that our created posts exist by their titles
        created_titles = [post["title"] for post in retrieved_posts["data"] if post["id"] in [cp.id for cp in created_posts]]
        assert len(created_titles) == 3


class TestUpdatePost:
    """Test post update operations."""

    @pytest.mark.asyncio
    async def test_update_post_success(self, async_db: AsyncSession, sample_post_data, sample_user):
        """Test successful post update."""
        # Create a post first
        post_create = PostCreate(**sample_post_data)
        post_internal_dict = post_create.model_dump()
        post_internal_dict["created_by_user_id"] = sample_user.id
        
        post_internal = PostCreateInternal(**post_internal_dict)
        created_post = await crud_posts.create(db=async_db, object=post_internal)
        
        # Update the post
        update_data = PostUpdate(title="Updated Title", text="Updated content")
        await crud_posts.update(
            db=async_db, 
            object=update_data, 
            id=created_post.id
        )
        
        # Verify the update by retrieving the updated record
        updated_post = await crud_posts.get(db=async_db, id=created_post.id)
        assert updated_post is not None
        assert updated_post["title"] == "Updated Title"
        assert updated_post["text"] == "Updated content"

    @pytest.mark.asyncio
    async def test_update_post_partial(self, async_db: AsyncSession, sample_post_data, sample_user):
        """Test partial post update."""
        # Create a post first
        post_create = PostCreate(**sample_post_data)
        post_internal_dict = post_create.model_dump()
        post_internal_dict["created_by_user_id"] = sample_user.id
        
        post_internal = PostCreateInternal(**post_internal_dict)
        created_post = await crud_posts.create(db=async_db, object=post_internal)
        
        # Update only the title
        update_data = PostUpdate(title="New Title Only")
        await crud_posts.update(
            db=async_db, 
            object=update_data, 
            id=created_post.id
        )
        
        # Verify the update by retrieving the updated record
        updated_post = await crud_posts.get(db=async_db, id=created_post.id)
        assert updated_post is not None
        assert updated_post["title"] == "New Title Only"
        assert updated_post["text"] == created_post.text  # Should remain unchanged
        assert updated_post["media_url"] == created_post.media_url  # Should remain unchanged


class TestDeletePost:
    """Test post deletion operations."""

    @pytest.mark.asyncio
    async def test_delete_post_success(self, async_db: AsyncSession, sample_post_data, sample_user):
        """Test successful post deletion."""
        # Create a post first
        post_create = PostCreate(**sample_post_data)
        post_internal_dict = post_create.model_dump()
        post_internal_dict["created_by_user_id"] = sample_user.id
        
        post_internal = PostCreateInternal(**post_internal_dict)
        created_post = await crud_posts.create(db=async_db, object=post_internal)
        
        # Delete the post (this will be a soft delete)
        await crud_posts.delete(db=async_db, id=created_post.id)
        
        # Verify post is soft deleted (still retrievable but marked as deleted)
        retrieved_post = await crud_posts.get(db=async_db, id=created_post.id)
        assert retrieved_post is not None
        assert retrieved_post["is_deleted"] is True
        assert retrieved_post["deleted_at"] is not None

    @pytest.mark.asyncio
    async def test_soft_delete_post(self, async_db: AsyncSession, sample_post_data, sample_user):
        """Test soft delete functionality."""
        # Create a post first
        post_create = PostCreate(**sample_post_data)
        post_internal_dict = post_create.model_dump()
        post_internal_dict["created_by_user_id"] = sample_user.id
        
        post_internal = PostCreateInternal(**post_internal_dict)
        created_post = await crud_posts.create(db=async_db, object=post_internal)
        
        # Soft delete the post by calling delete (which does soft delete)
        await crud_posts.delete(db=async_db, id=created_post.id)
        
        # Verify the soft delete by retrieving the updated record
        soft_deleted_post = await crud_posts.get(db=async_db, id=created_post.id)
        assert soft_deleted_post is not None
        assert soft_deleted_post["is_deleted"] is True
        assert soft_deleted_post["deleted_at"] is not None


class TestPostValidation:
    """Test post validation and constraints."""

    @pytest.mark.asyncio
    async def test_post_title_length_limit(self, async_db: AsyncSession, sample_user):
        """Test that post title respects length limit."""
        # Title should be limited to 30 characters
        long_title = "A" * 31  # 31 characters, exceeding limit
        
        post_data = {
            "title": long_title,
            "text": "Test content",
        }
        
        # This should raise a ValidationError due to title length
        with pytest.raises(Exception):  # Could be ValidationError or database constraint error
            post_create = PostCreate(**post_data)

    @pytest.mark.asyncio
    async def test_post_text_length_limit(self, async_db: AsyncSession, sample_user):
        """Test that post text respects length limit."""
        # Text should be limited to 63206 characters
        long_text = "A" * 63207  # 63207 characters, exceeding limit
        
        post_data = {
            "title": "Test Title",
            "text": long_text,
        }
        
        # This should raise a ValidationError due to text length
        with pytest.raises(Exception):  # Could be ValidationError or database constraint error
            post_create = PostCreate(**post_data)
