from __future__ import annotations
from typing import Optional
from uuid import UUID

from domain.uow.unit_of_work import UnitOfWork
from domain.repositories.author_repository import AuthorRepository
from domain.entities.catalog.author import Author
from utils.exceptions.not_found_error_exception import NotFoundErrorException

class AuthorService:
    """Casos de uso de Authors. Orquesta repos bajo una UoW (transacción)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.repo = AuthorRepository(uow.session)

    def create(self, *, full_name: str, bio: Optional[str]) -> Author:
        author = Author(full_name=full_name, bio=bio)
        self.repo.add(author)
        return author

    def list(self, *, q: Optional[str], skip: int, limit: int) -> list[Author]:
        return self.repo.search(q, skip=skip, limit=limit)

    def get(self, author_id: UUID) -> Author:
        author = self.repo.get(author_id)
        if not author:
            raise NotFoundErrorException("Autor no encontrado")
        return author

    def update(self, author_id: UUID, *, full_name: Optional[str], bio: Optional[str]) -> Author:
        author = self.repo.get(author_id, for_update=True)
        if not author:
            raise NotFoundErrorException("Autor no encontrado")

        if full_name is not None:
            author.full_name = full_name
        if bio is not None:
            author.bio = bio
        return author

    def delete(self, author_id: UUID) -> None:
        author = self.repo.get(author_id, for_update=True)
        if not author:
            raise NotFoundErrorException("Autor no encontrado")
        self.repo.delete(author)
