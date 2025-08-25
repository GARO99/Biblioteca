from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, status
from api.deps import get_uow
from api.schemas.book import BookCreate, BookUpdate, BookRead
from domain.entities.catalog.book import Book
from domain.services.book_service import BookService
from domain.uow.unit_of_work import UnitOfWork
from utils.exceptions.not_found_error_exception import NotFoundErrorException

router = APIRouter()

def _to_book_read(book: Book) -> BookRead:
    author_ids = [a.id for a in getattr(book, "authors", [])]
    genre_ids  = [g.id for g in getattr(book, "genres",  [])]
    return BookRead(
        id=book.id,
        title=book.title,
        isbn_13=getattr(book, "isbn_13", None),
        language=getattr(book, "language", None),
        published_year=getattr(book, "published_year", None),
        publisher_id=getattr(book, "publisher_id", None),
        author_ids=author_ids or None,
        genre_ids=genre_ids or None,
    )

@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, uow: UnitOfWork = Depends(get_uow)):
    svc = BookService(uow)
    book = svc.create(
        title=payload.title,
        isbn_13=payload.isbn_13,
        language=payload.language,
        published_year=payload.published_year,
        publisher_id=payload.publisher_id,
        author_ids=payload.author_ids,
        genre_ids=payload.genre_ids,
    )
    
    return _to_book_read(book)

@router.get("/", response_model=List[BookRead])
def list_books(
    q: Optional[str] = None, skip: int = 0, limit: int = 50,
    uow: UnitOfWork = Depends(get_uow),
):
    svc = BookService(uow)
    books = svc.list(q=q, skip=skip, limit=limit)
    return [_to_book_read(b) for b in books]

@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = BookService(uow)
    book = svc.get(book_id)
    if not book:
        raise NotFoundErrorException("Libro no encontrado")
    return _to_book_read(book)

@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: UUID, payload: BookUpdate, uow: UnitOfWork = Depends(get_uow)):
    svc = BookService(uow)
    book = svc.update(
            book_id,
            title=payload.title,
            isbn_13=payload.isbn_13,
            language=payload.language,
            published_year=payload.published_year,
            publisher_id=payload.publisher_id,
            author_ids=payload.author_ids,
            genre_ids=payload.genre_ids,
        )
    return _to_book_read(book)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = BookService(uow)
    svc.delete(book_id)
