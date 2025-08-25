from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import func

from domain.uow.unit_of_work import UnitOfWork
from domain.repositories.base_repository import BaseRepository
from domain.entities.users_traffic.fine import Fine
from domain.entities.users_traffic.member import Member
from domain.entities.users_traffic.loan import Loan
from utils.exceptions.not_found_error_exception import NotFoundErrorException
from utils.exceptions.app_exception import AppException


class FineService:
    """Casos de uso para multas (fines)."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.fine_repo   = BaseRepository[Fine](Fine, uow.session)
        self.member_repo = BaseRepository[Member](Member, uow.session)
        self.loan_repo   = BaseRepository[Loan](Loan, uow.session)

    def create(
        self,
        *,
        member_id: UUID,
        amount_cents: int,
        reason: Optional[str],
        loan_id: Optional[UUID],
    ) -> Fine:
        if amount_cents <= 0:
            raise AppException("amount_cents debe ser > 0")

        self._ensure_member_exists(member_id)
        if loan_id:
            self._ensure_loan_belongs_to_member(loan_id, member_id)

        fine = Fine(
            member_id=member_id,
            loan_id=loan_id,
            amount_cents=amount_cents,
            reason=reason,
            paid=False,
            paid_at=None,
        )
        self.fine_repo.add(fine)
        return fine

    def list(self, *, member_id: Optional[UUID], skip: int, limit: int) -> list[Fine]:
        filters = []
        if member_id:
            filters.append(Fine.member_id == member_id)
        return self.fine_repo.list(filters=filters, offset=skip, limit=limit)

    def get(self, fine_id: UUID) -> Fine:
        fine = self.fine_repo.get(fine_id)
        if not fine:
            raise NotFoundErrorException("Multa no encontrada")
        return fine

    def update(
        self,
        fine_id: UUID,
        *,
        amount_cents: Optional[int],
        reason: Optional[str],
        paid: Optional[bool],
        paid_at: Optional[datetime],
        loan_id: Optional[UUID],
    ) -> Fine:
        fine = self.fine_repo.get(fine_id, for_update=True)
        if not fine:
            raise NotFoundErrorException("Multa no encontrada")

        if amount_cents is not None:
            if amount_cents <= 0:
                raise AppException("amount_cents debe ser > 0")
            fine.amount_cents = amount_cents

        if reason is not None:
            fine.reason = reason

        if loan_id is not None:
            if loan_id:
                self._ensure_loan_belongs_to_member(loan_id, fine.member_id)
            fine.loan_id = loan_id

        if paid is not None:
            if paid and not paid_at:
                fine.paid = True
                fine.paid_at = self._now()
            elif not paid:
                fine.paid = False
                fine.paid_at = None
            else:
                fine.paid = True
                fine.paid_at = paid_at
        elif paid_at is not None:
            fine.paid = True
            fine.paid_at = paid_at

        return fine

    def pay(self, fine_id: UUID, *, paid_at: Optional[datetime]) -> Fine:
        fine = self.fine_repo.get(fine_id, for_update=True)
        if not fine:
            raise NotFoundErrorException("Multa no encontrada")
        if fine.paid:
            raise AppException("La multa ya está pagada")

        fine.paid = True
        fine.paid_at = paid_at or self._now()
        return fine

    def delete(self, fine_id: UUID) -> None:
        fine = self.fine_repo.get(fine_id, for_update=True)
        if not fine:
            raise NotFoundErrorException("Multa no encontrada")
        self.fine_repo.delete(fine)

    def _ensure_member_exists(self, member_id: UUID) -> None:
        if not self.member_repo.get(member_id):
            raise NotFoundErrorException("Miembro no encontrado")

    def _ensure_loan_belongs_to_member(self, loan_id: UUID, member_id: UUID) -> None:
        loan = self.loan_repo.get(loan_id)
        if not loan:
            raise NotFoundErrorException("Préstamo no encontrado")
        if loan.member_id != member_id:
            raise AppException("El préstamo no pertenece al miembro indicado")

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)