from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy import func

from domain.uow.unit_of_work import UnitOfWork
from domain.repositories.base_repository import BaseRepository
from domain.entities.catalog.genre import Genre
from utils.exceptions.not_found_error_exception import NotFoundErrorException
from utils.exceptions.duplicated_error_exception import DuplicatedErrorException


class GenreService:
    """Casos de uso para géneros (sin lógica HTTP)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.repo = BaseRepository[Genre](Genre, uow.session)

    def create(self, *, name: str, description: Optional[str]) -> Genre:
        if self._exists_name_ci(name):
            raise DuplicatedErrorException("El nombre del género ya existe")
        genre = Genre(name=name, description=description)
        self.repo.add(genre)
        return genre

    def list(self, *, q: Optional[str], skip: int, limit: int) -> list[Genre]:
        filters = []
        if q:
            filters.append(Genre.name.like(f"%{q}%"))
        return self.repo.list(filters=filters, offset=skip, limit=limit)

    def get(self, genre_id: UUID) -> Genre:
        genre = self.repo.get(genre_id)
        if not genre:
            raise NotFoundErrorException("Género no encontrado")
        return genre

    def update(self, genre_id: UUID, *, name: Optional[str], description: Optional[str]) -> Genre:
        genre = self.repo.get(genre_id, for_update=True)
        if not genre:
            raise NotFoundErrorException("Género no encontrado")

        if name is not None and name != genre.name:
            if self._exists_name_ci(name):
                raise DuplicatedErrorException("El nombre del género ya existe")
            genre.name = name
        if description is not None:
            genre.description = description
        return genre

    def delete(self, genre_id: UUID) -> None:
        genre = self.repo.get(genre_id, for_update=True)
        if not genre:
            raise NotFoundErrorException("Género no encontrado")
        self.repo.delete(genre)

    
    def _exists_name_ci(self, name: str) -> bool:
        return self.repo.exists(filters=[func.lower(Genre.name) == name.lower()])