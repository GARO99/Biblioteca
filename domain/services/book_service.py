from __future__ import annotations
from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from domain.uow.unit_of_work import UnitOfWork
from domain.repositories.book_repository import BookRepository
from domain.entities.catalog.book import Book
from domain.entities.catalog.author import Author
from domain.entities.catalog.genre import Genre
from utils.exceptions.duplicated_error_exception import DuplicatedErrorException
from utils.exceptions.not_found_error_exception import NotFoundErrorException

class BookService:
    """Orquesta casos de uso de Books sobre una UoW y repos. No usa HTTP aquí."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.repository = BookRepository(uow.session)

    def create(
        self,
        *,
        title: str,
        isbn_13: Optional[str],
        language: Optional[str],
        published_year: Optional[int],
        publisher_id: Optional[UUID],
        author_ids: Optional[Sequence[UUID]],
        genre_ids: Optional[Sequence[UUID]],
    ) -> Book:
        if isbn_13:
            existing = self.repository.find_by_isbn13(isbn_13)
            if existing:
                raise DuplicatedErrorException("ISBN ya existe")

        authors = self._load_authors(author_ids)
        genres  = self._load_genres(genre_ids)

        book = Book(
            title=title,
            isbn_13=isbn_13,
            language=language,
            published_year=published_year,
            publisher_id=publisher_id,
        )
        book.authors = authors
        book.genres  = genres

        self.repository.add(book)

        return book

    def list(
        self,
        *,
        q: Optional[str],
        skip: int,
        limit: int,
    ) -> list[Book]:
        filters = []
        if q:
            filters.append(Book.title.like(f"%{q}%"))
        return self.repository.list(
            filters=filters,
            offset=skip,
            limit=limit,
            options=(selectinload(Book.authors), selectinload(Book.genres)),
        )

    def get(self, book_id: UUID) -> Optional[Book]:
        # eager básico para leer autores/géneros también
        return self.repository.get(
            book_id,
            options=(selectinload(Book.authors), selectinload(Book.genres)),
        )

    def update(
        self,
        book_id: UUID,
        *,
        title: Optional[str],
        isbn_13: Optional[str],
        language: Optional[str],
        published_year: Optional[int],
        publisher_id: Optional[UUID],
        author_ids: Optional[Sequence[UUID]],
        genre_ids: Optional[Sequence[UUID]],
    ) -> Book:
        book = self.repository.get(book_id, for_update=True)
        if not book:
            raise NotFoundErrorException("Libro no encontrado")

        if isbn_13 and isbn_13 != getattr(book, "isbn_13", None):
            existing = self.repository.find_by_isbn13(isbn_13)
            if existing and existing.id != book_id:
                raise DuplicatedErrorException("ISBN ya existe")

        if title is not None:          book.title = title
        if isbn_13 is not None:        book.isbn_13 = isbn_13
        if language is not None:       book.language = language
        if published_year is not None: book.published_year = published_year
        if publisher_id is not None:   book.publisher_id = publisher_id

        if author_ids is not None:
            book.authors = self._load_authors(author_ids)
        if genre_ids is not None:
            book.genres = self._load_genres(genre_ids)

        return book

    def delete(self, book_id: UUID) -> None:
        book = self.repository.get(book_id, for_update=True)
        if not book:
            raise NotFoundErrorException("Libro no encontrado")
        self.repository.delete(book)

    def _load_authors(self, ids: Optional[Sequence[UUID]]) -> list[Author]:
        if not ids:
            return []
        rows = self.uow.session.execute(
            select(Author).where(Author.id.in_(list(ids)))
        ).scalars().all()
        if len(rows) != len(set(ids)):
            missing = set(ids) - {a.id for a in rows}
            raise NotFoundErrorException(f"Autores no encontrados: {', '.join(map(str, missing))}")
        return rows

    def _load_genres(self, ids: Optional[Sequence[UUID]]) -> list[Genre]:
        if not ids:
            return []
        rows = self.uow.session.execute(
            select(Genre).where(Genre.id.in_(list(ids)))
        ).scalars().all()
        if len(rows) != len(set(ids)):
            missing = set(ids) - {g.id for g in rows}
            raise NotFoundErrorException(f"Géneros no encontrados: {', '.join(map(str, missing))}")
        return rows