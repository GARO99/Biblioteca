from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import func

from domain.uow.unit_of_work import UnitOfWork
from domain.repositories.base_repository import BaseRepository
from domain.entities.users_traffic.hold import Hold
from domain.entities.catalog.book import Book
from domain.entities.users_traffic.member import Member
from domain.entities.inventory.copy import Copy
from domain.enums.hold_status import HoldStatus
from domain.enums.copy_status import CopyStatus
from utils.exceptions.not_found_error_exception import NotFoundErrorException
from utils.exceptions.duplicated_error_exception import DuplicatedErrorException
from utils.exceptions.app_exception import AppException


class HoldService:
    """Casos de uso para reservas (holds)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.hold_repo   = BaseRepository[Hold](Hold, uow.session)
        self.book_repo   = BaseRepository[Book](Book, uow.session)
        self.member_repo = BaseRepository[Member](Member, uow.session)
        self.copy_repo   = BaseRepository[Copy](Copy, uow.session)

    def place(self, *, member_id: UUID, book_id: UUID) -> Hold:
        self._ensure_member_and_book(member_id, book_id)
        if self._has_active_hold(member_id, book_id):
            raise DuplicatedErrorException("Ya existe un hold activo para este libro y miembro")

        hold = Hold(
            member_id=member_id,
            book_id=book_id,
            status=HoldStatus.ACTIVE.value,
            placed_at=datetime.now(timezone.utc),
        )
        self.hold_repo.add(hold)
        return hold

    def cancel(self, hold_id: UUID) -> Hold:
        hold = self.hold_repo.get(hold_id, for_update=True)
        if not hold:
            raise NotFoundErrorException("Hold no encontrado")
        if hold.status == HoldStatus.CANCELLED.value:
            return hold
        if hold.status == HoldStatus.FULFILLED.value and hold.fulfilled_copy_id:
            c = self.copy_repo.get(hold.fulfilled_copy_id, for_update=True)
            if c and c.status == CopyStatus.RESERVED.value:
                c.status = CopyStatus.AVAILABLE.value
        hold.status = HoldStatus.CANCELLED.value
        return hold

    def fulfill(self, hold_id: UUID, *, copy_id: UUID) -> Hold:
        hold = self.hold_repo.get(hold_id, for_update=True)
        if not hold:
            raise NotFoundErrorException("Hold no encontrado")
        if hold.status != HoldStatus.ACTIVE.value:
            raise AppException("Solo se pueden cumplir holds activos")

        c = self._lock_copy_available_for_book(copy_id, hold.book_id)
        c.status = CopyStatus.RESERVED.value
        hold.fulfilled_copy_id = c.id
        hold.status = HoldStatus.FULFILLED.value
        return hold

    def list(self, *, member_id: Optional[UUID], status_filter: Optional[str],
             skip: int, limit: int) -> list[Hold]:
        filters = []
        if member_id:
            filters.append(Hold.member_id == member_id)
        if status_filter is not None:
            filters.append(Hold.status == self._parse_status(status_filter))
        return self.hold_repo.list(filters=filters, offset=skip, limit=limit)

    def get(self, hold_id: UUID) -> Hold:
        hold = self.hold_repo.get(hold_id)
        if not hold:
            raise NotFoundErrorException("Hold no encontrado")
        return hold

    def delete(self, hold_id: UUID) -> None:
        hold = self.hold_repo.get(hold_id, for_update=True)
        if not hold:
            raise NotFoundErrorException("Hold no encontrado")
        if hold.status == HoldStatus.FULFILLED.value and hold.fulfilled_copy_id:
            c = self.copy_repo.get(hold.fulfilled_copy_id, for_update=True)
            if c and c.status == CopyStatus.RESERVED.value:
                c.status = CopyStatus.AVAILABLE.value
        self.hold_repo.delete(hold)

    def _parse_status(self, status: Optional[str | HoldStatus]) -> Optional[str]:
        if status is None:
            return None
        if isinstance(status, HoldStatus):
            return status.value
        try:
            return HoldStatus(status).value
        except ValueError as e:
            raise AppException("status inválido") from e

    def _ensure_member_and_book(self, member_id: UUID, book_id: UUID) -> None:
        if not self.member_repo.get(member_id):
            raise NotFoundErrorException("Miembro no encontrado")
        if not self.book_repo.get(book_id):
            raise NotFoundErrorException("Libro no encontrado")

    def _has_active_hold(self, member_id: UUID, book_id: UUID) -> bool:
        return self.hold_repo.exists(filters=[
            Hold.member_id == member_id,
            Hold.book_id == book_id,
            Hold.status == HoldStatus.ACTIVE.value
        ])

    def _lock_copy_available_for_book(self, copy_id: UUID, book_id: UUID) -> Copy:
        c = self.copy_repo.get(copy_id, for_update=True)  # lock fila
        if not c:
            raise NotFoundErrorException("Copia no encontrada")
        if c.book_id != book_id:
            raise AppException("La copia no pertenece al libro del hold")
        if c.status != CopyStatus.AVAILABLE.value:
            raise AppException("La copia no está disponible")
        return c
