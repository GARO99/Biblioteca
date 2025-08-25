from __future__ import annotations
from typing import Optional, Sequence
from sqlalchemy import select
from domain.repositories.base_repository import BaseRepository
from domain.entities.catalog.author import Author

class AuthorRepository(BaseRepository[Author]):
    def __init__(self, session):
        super().__init__(Author, session)

    def find_by_name(self, full_name: str) -> Optional[Author]:
        stmt = select(Author).where(Author.full_name == full_name)
        return self.session.execute(stmt).scalar_one_or_none()

    def search(self, q: Optional[str], *, skip: int, limit: int) -> list[Author]:
        filters: Sequence = ()
        if q:
            filters = (*filters, Author.full_name.like(f"%{q}%"))
        return self.list(filters=filters, offset=skip, limit=limit)
