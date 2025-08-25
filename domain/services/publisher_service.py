from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy import func

from domain.uow.unit_of_work import UnitOfWork
from domain.repositories.base_repository import BaseRepository
from domain.entities.catalog.publisher import Publisher
from utils.exceptions.not_found_error_exception import NotFoundErrorException
from utils.exceptions.duplicated_error_exception import DuplicatedErrorException


class PublisherService:
    """Casos de uso para editoriales (publishers)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.repo = BaseRepository[Publisher](Publisher, uow.session)


    def create(self, *, name: str, website: Optional[str]) -> Publisher:
        if self._name_exists_ci(name):
            raise DuplicatedErrorException("El nombre del publisher ya existe")
        pub = Publisher(name=name, website=website)
        self.repo.add(pub)
        return pub

    def list(self, *, q: Optional[str], skip: int, limit: int) -> list[Publisher]:
        filters = []
        if q:
            filters.append(Publisher.name.like(f"%{q}%"))
        return self.repo.list(filters=filters, offset=skip, limit=limit)

    def get(self, publisher_id: UUID) -> Publisher:
        pub = self.repo.get(publisher_id)
        if not pub:
            raise NotFoundErrorException("Publisher no encontrado")
        return pub

    def update(self, publisher_id: UUID, *, name: Optional[str], website: Optional[str]) -> Publisher:
        pub = self.repo.get(publisher_id, for_update=True)
        if not pub:
            raise NotFoundErrorException("Publisher no encontrado")

        if name is not None and name != pub.name:
            if self._name_exists_ci(name):
                raise DuplicatedErrorException("El nombre del publisher ya existe")
            pub.name = name

        if website is not None:
            pub.website = website

        return pub

    def delete(self, publisher_id: UUID) -> None:
        pub = self.repo.get(publisher_id, for_update=True)
        if not pub:
            raise NotFoundErrorException("Publisher no encontrado")
        self.repo.delete(pub)

    def _name_exists_ci(self, name: str) -> bool:
        return self.repo.exists(filters=[func.lower(Publisher.name) == name.lower()])