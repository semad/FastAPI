from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class BookBase(BaseModel):
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
        Field(max_length=50, examples=["Fiction", "Science Fiction", "Mystery"], default=None),
    ]
    pages: Annotated[
        int | None,
        Field(ge=1, examples=[180], default=None),
    ]
    cover_image_url: Annotated[
        str | None,
        Field(pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", examples=["https://example.com/cover.jpg"], default=None),
    ]
    folder_path: Annotated[
        str | None,
        Field(max_length=500, examples=["/books/fiction/classics", "/uploads/2024/08"], default=None),
    ]
    file_size_bytes: Annotated[
        int | None,
        Field(ge=0, examples=[1024000, 2048000], default=None),
    ]
    content_hash: Annotated[
        str | None,
        Field(max_length=64, pattern=r"^[a-fA-F0-9]+$", examples=["a1b2c3d4e5f6"], default=None),
    ]


class Book(TimestampSchema, BookBase, UUIDSchema, PersistentDeletion):
    created_by_user_id: int | None = None


class BookRead(BaseModel):
    id: int
    title: Annotated[str, Field(min_length=1, max_length=200, examples=["The Great Gatsby"])]
    author: Annotated[str, Field(min_length=1, max_length=100, examples=["F. Scott Fitzgerald"])]
    description: Annotated[
        str | None,
        Field(examples=["A story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan."], default=None),
    ]
    isbn: Annotated[
        str | None,
        Field(examples=["978-0-7475-3269-9"], default=None),
    ]
    publication_year: Annotated[
        int | None,
        Field(examples=[1925], default=None),
    ]
    genre: Annotated[
        str | None,
        Field(examples=["Fiction"], default=None),
    ]
    pages: Annotated[
        int | None,
        Field(examples=[180], default=None),
    ]
    cover_image_url: Annotated[
        str | None,
        Field(examples=["https://example.com/cover.jpg"], default=None),
    ]
    folder_path: Annotated[
        str | None,
        Field(examples=["/books/fiction/classics", "/uploads/2024/08"], default=None),
    ]
    file_size_bytes: Annotated[
        int | None,
        Field(examples=[1024000, 2048000], default=None),
    ]
    content_hash: Annotated[
        str | None,
        Field(examples=["a1b2c3d4e5f6"], default=None),
    ]
    created_by_user_id: int | None = None
    created_at: datetime


class BookCreate(BookBase):
    model_config = ConfigDict(extra="forbid")


class BookCreateInternal(BookCreate):
    created_by_user_id: int | None = None


class BookUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[
        str | None,
        Field(min_length=1, max_length=200, examples=["The Great Gatsby"], default=None),
    ]
    author: Annotated[
        str | None,
        Field(min_length=1, max_length=100, examples=["F. Scott Fitzgerald"], default=None),
    ]
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


class BookUpdateInternal(BookUpdate):
    updated_at: datetime


class BookDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
