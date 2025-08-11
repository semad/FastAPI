from fastcrud import FastCRUD

from ..models.book import Book
from ..schemas.book import BookCreateInternal, BookDelete, BookRead, BookUpdate, BookUpdateInternal

CRUDBook = FastCRUD[Book, BookCreateInternal, BookUpdate, BookUpdateInternal, BookDelete, BookRead]
crud_books = CRUDBook(Book)
