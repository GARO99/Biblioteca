from __future__ import annotations
from uuid import UUID
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from domain.uow.unit_of_work import UnitOfWork
from domain.entities.catalog.book import Book
from domain.semantic.book_lc_openai_index import BookOpenAILCIndex

class BookSemanticOpenAIService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.idx = BookOpenAILCIndex(uow.session)

    def search(self, q: str, k: int = 10) -> list[Book]:
        ids = [UUID(x) for x in self.idx.search(q, k=k)]
        if not ids:
            return []
        order = {bid: i for i, bid in enumerate(ids)}
        rows = (
            self.uow.session.execute(
                select(Book)
                .where(Book.id.in_(ids))
                .options(selectinload(Book.authors), selectinload(Book.genres))
            ).scalars().all()
        )
        rows.sort(key=lambda b: order[b.id])
        return rows

    def rebuild(self) -> None:
        self.idx.rebuild()
