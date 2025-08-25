from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .base_repository import BaseRepository
from domain.entities.catalog.book import Book

class BookRepository(BaseRepository[Book]):
    def __init__(self, session): super().__init__(Book, session)

    def find_by_isbn13(self, isbn: str) -> Book | None:
        stmt = select(Book).where(Book.isbn_13 == isbn)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_with_authors(self, **kwargs) -> list[Book]:
        opts = kwargs.pop("options", ())
        return self.list(options=(*opts, selectinload(Book.authors)), **kwargs)
