import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    isbn: Mapped[str | None] = mapped_column(String(13), unique=True, index=True, default=None)
    publication_year: Mapped[int | None] = mapped_column(default=None)
    genre: Mapped[str | None] = mapped_column(String(50), default=None)
    pages: Mapped[int | None] = mapped_column(default=None)
    cover_image_url: Mapped[str | None] = mapped_column(String, default=None)
    folder_path: Mapped[str | None] = mapped_column(String(500), default=None, index=True)
    file_size_bytes: Mapped[int | None] = mapped_column(default=None)
    content_hash: Mapped[str | None] = mapped_column(String(64), default=None, index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True, default=None)
    
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, primary_key=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
