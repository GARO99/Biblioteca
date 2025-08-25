from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy import func
from domain.uow.unit_of_work import UnitOfWork
from domain.repositories.base_repository import BaseRepository
from domain.entities.inventory.copy import Copy
from domain.entities.catalog.book import Book
from domain.enums.copy_status import CopyStatus
from utils.exceptions.not_found_error_exception import NotFoundErrorException
from utils.exceptions.duplicated_error_exception import DuplicatedErrorException
from utils.exceptions.app_exception import AppException


class CopyService:
    """Casos de uso para copias físicas de libros."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.copy_repo = BaseRepository[Copy](Copy, uow.session)
        self.book_repo = BaseRepository[Book](Book, uow.session)

    def create(
        self,
        *,
        book_id: UUID,
        inventory_code: str,
        status: CopyStatus = CopyStatus.AVAILABLE,
        location: Optional[str] = None,
    ) -> Copy:
        if not self.book_repo.get(book_id):
            raise NotFoundErrorException("Libro no encontrado")

        if self._inventory_exists_ci(inventory_code):
            raise DuplicatedErrorException("El código de inventario ya existe")

        copy = Copy(
            book_id=book_id,
            inventory_code=inventory_code,
            status=status.value if isinstance(status, CopyStatus) else str(status),
            location=location,
        )
        self.copy_repo.add(copy)
        return copy

    def list(
        self,
        *,
        book_id: Optional[UUID],
        status_filter: Optional[str],
        skip: int,
        limit: int,
    ) -> list[Copy]:
        filters = []
        if book_id:
            filters.append(Copy.book_id == book_id)
        if status_filter is not None:
            filters.append(Copy.status == self._parse_status(status_filter))
        return self.copy_repo.list(filters=filters, offset=skip, limit=limit)

    def get(self, copy_id: UUID) -> Copy:
        c = self.copy_repo.get(copy_id)
        if not c:
            raise NotFoundErrorException("Copia no encontrada")
        return c

    def update(
        self,
        copy_id: UUID,
        *,
        inventory_code: Optional[str],
        status: Optional[str],
        location: Optional[str],
    ) -> Copy:
        c = self.copy_repo.get(copy_id, for_update=True)
        if not c:
            raise NotFoundErrorException("Copia no encontrada")

        if inventory_code is not None and inventory_code != c.inventory_code:
            if self._inventory_exists_ci(inventory_code):
                raise DuplicatedErrorException("El código de inventario ya existe")
            c.inventory_code = inventory_code

        if status is not None:
            c.status = self._parse_status(status)

        if location is not None:
            c.location = location

        return c

    def delete(self, copy_id: UUID) -> None:
        c = self.copy_repo.get(copy_id, for_update=True)
        if not c:
            raise NotFoundErrorException("Copia no encontrada")
        self.copy_repo.delete(c)

    def _inventory_exists_ci(self, inventory_code: str) -> bool:
        return self.copy_repo.exists(
            filters=[func.lower(Copy.inventory_code) == inventory_code.lower()]
        )

    def _parse_status(self, status: Optional[str]) -> Optional[str]:
        if status is None:
            return None
        try:
            return CopyStatus(status).value if not isinstance(status, CopyStatus) else status.value
        except ValueError as e:
            raise AppException("status inválido") from e