from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import ForbiddenException, NotFoundException, DuplicateValueException
from ...core.utils.cache import cache, no_cache
from ...crud.crud_books import crud_books
from ...crud.crud_users import crud_users
from ...schemas.book import BookCreate, BookCreateInternal, BookRead, BookUpdate
from ...schemas.user import UserRead

router = APIRouter(tags=["books"])

@router.get("/books", response_model=PaginatedListResponse[BookRead])
@router.post("/books", response_model=PaginatedListResponse[BookRead])
@cache(
    key_prefix="public_books:page_{page}:items_per_page:{items_per_page}",
    resource_id_name="page",
    expiration=300,
)
async def read_all_books(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
) -> dict:
    books_data = await crud_books.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=books_data, page=page, items_per_page=items_per_page)
    return response



@router.post("/{username}/book", response_model=BookRead, status_code=201)
async def write_book(
    request: Request,
    username: str,
    book: BookCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> BookRead:
    db_user = await crud_users.get(db=db, username=username, is_deleted=False, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    # Handle case where crud_users.get returns a dict instead of UserRead model
    if isinstance(db_user, dict):
        user_id = db_user.get("id")
        if user_id is None:
            raise NotFoundException("User ID not found")
    else:
        db_user = cast(UserRead, db_user)
        user_id = db_user.id

    if current_user["id"] != user_id:
        raise ForbiddenException()

    # Check for duplicate ISBN if provided
    if book.isbn:
        existing_book = await crud_books.exists(db=db, isbn=book.isbn, is_deleted=False)
        if existing_book:
            raise DuplicateValueException("Book with this ISBN already exists")

    book_internal_dict = book.model_dump()
    book_internal_dict["created_by_user_id"] = user_id

    book_internal = BookCreateInternal(**book_internal_dict)
    created_book = await crud_books.create(db=db, object=book_internal)

    book_read = await crud_books.get(db=db, id=created_book.id, schema_to_select=BookRead)
    if book_read is None:
        raise NotFoundException("Created book not found")

    return cast(BookRead, book_read)


@router.post("/{username}/books", response_model=PaginatedListResponse[BookRead])
@router.get("/{username}/books", response_model=PaginatedListResponse[BookRead])
@cache(
    key_prefix="{username}_books:page_{page}:items_per_page:{items_per_page}",
    resource_id_name="username",
    expiration=0,

)
async def read_books(
    request: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
) -> dict:
    db_user = await crud_users.get(db=db, username=username, is_deleted=False, schema_to_select=UserRead)
    if not db_user:
        raise NotFoundException("User not found")

    # Handle case where crud_users.get returns a dict instead of UserRead model
    if isinstance(db_user, dict):
        user_id = db_user.get("id")
        if user_id is None:
            raise NotFoundException("User ID not found")
    else:
        db_user = cast(UserRead, db_user)
        user_id = db_user.id

    books_data = await crud_books.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        created_by_user_id=user_id,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=books_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/{username}/book/{id}", response_model=BookRead)
@cache(key_prefix="{username}_book_cache", resource_id_name="id")
async def read_book(
    request: Request, username: str, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> BookRead:
    db_user = await crud_users.get(db=db, username=username, is_deleted=False, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    # Handle case where crud_users.get returns a dict instead of UserRead model
    if isinstance(db_user, dict):
        user_id = db_user.get("id")
        if user_id is None:
            raise NotFoundException("User ID not found")
    else:
        db_user = cast(UserRead, db_user)
        user_id = db_user.id

    db_book = await crud_books.get(
        db=db, id=id, created_by_user_id=user_id, is_deleted=False, schema_to_select=BookRead
    )
    if db_book is None:
        raise NotFoundException("Book not found")

    return cast(BookRead, db_book)


@router.patch("/{username}/book/{id}")
@cache("{username}_book_cache", resource_id_name="id", pattern_to_invalidate_extra=["{username}_books:*"])
async def patch_book(
    request: Request,
    username: str,
    id: int,
    values: BookUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    db_user = await crud_users.get(db=db, username=username, is_deleted=False, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    # Handle case where crud_users.get returns a dict instead of UserRead model
    if isinstance(db_user, dict):
        user_id = db_user.get("id")
        if user_id is None:
            raise NotFoundException("User ID not found")
    else:
        db_user = cast(UserRead, db_user)
        user_id = db_user.id

    if current_user["id"] != user_id:
        raise ForbiddenException()

    db_book = await crud_books.get(db=db, id=id, created_by_user_id=user_id, is_deleted=False)
    if db_book is None:
        raise NotFoundException("Book not found")

    # Check for duplicate ISBN if updating
    if values.isbn and values.isbn != db_book.get("isbn"):
        existing_book = await crud_books.exists(db=db, isbn=values.isbn, is_deleted=False)
        if existing_book:
            raise DuplicateValueException("Book with this ISBN already exists")

    await crud_books.update(db=db, object=values, id=id, created_by_user_id=user_id)
    return {"message": "Book updated successfully"}


@router.delete("/{username}/book/{id}")
@cache("{username}_book_cache", resource_id_name="id", to_invalidate_extra={"{username}_books": "{username}"})
async def erase_book(
    request: Request,
    username: str,
    id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    db_user = await crud_users.get(db=db, username=username, is_deleted=False, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    # Handle case where crud_users.get returns a dict instead of UserRead model
    if isinstance(db_user, dict):
        user_id = db_user.get("id")
        if user_id is None:
            raise NotFoundException("User ID not found")
    else:
        db_user = cast(UserRead, db_user)
        user_id = db_user.id

    if current_user["id"] != user_id:
        raise ForbiddenException()

    db_book = await crud_books.get(db=db, id=id, created_by_user_id=user_id, is_deleted=False)
    if db_book is None:
        raise NotFoundException("Book not found")

    await crud_books.delete(db=db, id=id, created_by_user_id=user_id)
    return {"message": "Book deleted successfully"}


@router.delete("/{username}/db_book/{id}", dependencies=[Depends(get_current_superuser)])
@cache("{username}_book_cache", resource_id_name="id", to_invalidate_extra={"{username}_books": "{username}"})
async def erase_db_book(
    request: Request, username: str, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_user = await crud_users.get(db=db, username=username, is_deleted=False, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    # Handle case where crud_users.get returns a dict instead of UserRead model
    if isinstance(db_user, dict):
        user_id = db_user.get("id")
        if user_id is None:
            raise NotFoundException("User ID not found")
    else:
        db_user = cast(UserRead, db_user)
        user_id = db_user.id

    db_book = await crud_books.get(db=db, id=id, created_by_user_id=user_id)
    if db_book is None:
        raise NotFoundException("Book not found")

    await crud_books.db_delete(db=db, id=id, created_by_user_id=user_id)
    return {"message": "Book permanently deleted successfully"}


@router.get("/book/{id}", response_model=BookRead)
@cache(key_prefix="public_book_cache", resource_id_name="id")
async def read_public_book(
    request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> BookRead:
    db_book = await crud_books.get(db=db, id=id, is_deleted=False, schema_to_select=BookRead)
    if db_book is None:
        raise NotFoundException("Book not found")

    return cast(BookRead, db_book)
