from typing import Annotated

from crudadmin import CRUDAdmin
from crudadmin.admin_interface.model_view import PasswordTransformer
from pydantic import BaseModel, Field

from ..core.security import get_password_hash
from ..models.book import Book
from ..models.post import Post
from ..models.tier import Tier
from ..models.user import User
from ..schemas.book import BookCreate, BookUpdate
from ..schemas.post import PostUpdate
from ..schemas.tier import TierCreate, TierUpdate
from ..schemas.user import UserCreate, UserUpdate


class PostCreateAdmin(BaseModel):
    title: Annotated[str, Field(min_length=2, max_length=30, examples=["This is my post"])]
    text: Annotated[str, Field(min_length=1, max_length=63206, examples=["This is the content of my post."])]
    created_by_user_id: int
    media_url: Annotated[
        str | None,
        Field(pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", examples=["https://www.postimageurl.com"], default=None),
    ]


class BookCreateAdmin(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=200, examples=["The Great Gatsby"])]
    author: Annotated[str, Field(min_length=1, max_length=100, examples=["F. Scott Fitzgerald"])]
    description: Annotated[
        str | None,
        Field(max_length=2000, examples=["A story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan."], default=None),
    ]
    isbn: Annotated[
        str | None,
        Field(pattern=r"^[0-9X-]{10,13}$", examples=["978-0-7475-3269-9"], default=None),
    ]
    publication_year: Annotated[
        int | None,
        Field(ge=1800, le=2030, examples=[1925], default=None),
    ]
    genre: Annotated[
        str | None,
        Field(max_length=50, examples=["Fiction"], default=None),
    ]
    pages: Annotated[
        int | None,
        Field(ge=1, examples=[180], default=None),
    ]
    cover_image_url: Annotated[
        str | None,
        Field(pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", examples=["https://example.com/cover.jpg"], default=None),
    ]
    created_by_user_id: int | None = None


def register_admin_views(admin: CRUDAdmin) -> None:
    """Register all models and their schemas with the admin interface.

    This function adds all available models to the admin interface with appropriate
    schemas and permissions.
    """

    password_transformer = PasswordTransformer(
        password_field="password",
        hashed_field="hashed_password",
        hash_function=get_password_hash,
        required_fields=["name", "username", "email"],
    )

    admin.add_view(
        model=User,
        create_schema=UserCreate,
        update_schema=UserUpdate,
        allowed_actions={"view", "create", "update"},
        password_transformer=password_transformer,
    )

    admin.add_view(
        model=Tier,
        create_schema=TierCreate,
        update_schema=TierUpdate,
        allowed_actions={"view", "create", "update", "delete"},
    )

    admin.add_view(
        model=Post,
        create_schema=PostCreateAdmin,
        update_schema=PostUpdate,
        allowed_actions={"view", "create", "update", "delete"},
    )

    admin.add_view(
        model=Book,
        create_schema=BookCreateAdmin,
        update_schema=BookUpdate,
        allowed_actions={"view", "create", "update", "delete"},
    )
