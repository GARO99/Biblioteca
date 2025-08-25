from __future__ import annotations
from typing import Optional, Sequence
from uuid import UUID
from datetime import datetime, timezone

from domain.uow.unit_of_work import UnitOfWork
from domain.repositories.base_repository import BaseRepository
from domain.entities.users_traffic.loan import Loan
from domain.entities.users_traffic.member import Member
from domain.entities.inventory.copy import Copy
from domain.enums.loan_status import LoanStatus
from domain.enums.copy_status import CopyStatus
from utils.exceptions.not_found_error_exception import NotFoundErrorException
from utils.exceptions.duplicated_error_exception import DuplicatedErrorException
from utils.exceptions.app_exception import AppException

class LoanService:
    """Casos de uso para préstamos."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.loan_repo  = BaseRepository[Loan](Loan, uow.session)
        self.copy_repo  = BaseRepository[Copy](Copy, uow.session)
        self.member_repo = BaseRepository[Member](Member, uow.session)

    def create(self, *, copy_id: UUID, member_id: UUID, due_date: datetime) -> Loan:
        self._ensure_member_exists(member_id)
        copy = self._ensure_copy_available(copy_id)
        self._ensure_no_open_loan_for_copy(copy_id)

        loan = Loan(
            copy_id=copy_id,
            member_id=member_id,
            loan_date=datetime.now(timezone.utc),
            due_date=due_date,
            status=LoanStatus.OPEN.value,
        )
        self.loan_repo.add(loan)

        copy.status = CopyStatus.LOANED.value
        return loan

    def return_loan(self, loan_id: UUID, *, return_date: Optional[datetime]) -> Loan:
        loan = self.loan_repo.get(loan_id, for_update=True)
        if not loan:
            raise NotFoundErrorException("Préstamo no encontrado")
        if loan.status not in (LoanStatus.OPEN.value, LoanStatus.LATE.value):
            raise AppException("El préstamo no está abierto")

        # liberar la copia bajo lock
        copy = self.copy_repo.get(loan.copy_id, for_update=True)
        if not copy:
            raise NotFoundErrorException("Copia no encontrada")

        loan.return_date = return_date or datetime.now(timezone.utc)
        loan.status = LoanStatus.RETURNED.value
        # Si la copia no fue marcada LOST/DAMAGED por otro flujo, vuelve a AVAILABLE
        if copy.status == CopyStatus.LOANED.value:
            copy.status = CopyStatus.AVAILABLE.value
        return loan

    def list(self, *, member_id: Optional[UUID], status_filter: Optional[str], skip: int, limit: int) -> list[Loan]:
        filters: list = []
        if member_id:
            filters.append(Loan.member_id == member_id)
        if status_filter is not None:
            filters.append(Loan.status == self._parse_status(status_filter))
        return self.loan_repo.list(filters=filters, offset=skip, limit=limit)

    def get(self, loan_id: UUID) -> Loan:
        loan = self.loan_repo.get(loan_id)
        if not loan:
            raise NotFoundErrorException("Préstamo no encontrado")
        return loan

    def update(
        self,
        loan_id: UUID,
        *,
        due_date: Optional[datetime],
        status: Optional[LoanStatus | str],
    ) -> Loan:
        loan = self.loan_repo.get(loan_id, for_update=True)
        if not loan:
            raise NotFoundErrorException("Préstamo no encontrado")

        if due_date is not None:
            loan.due_date = due_date

        if status is not None:
            new_status = self._parse_status(status)
            if new_status == LoanStatus.LOST.value:
                # marcar la copia como perdida
                copy = self.copy_repo.get(loan.copy_id, for_update=True)
                if not copy:
                    raise NotFoundErrorException("Copia no encontrada")
                copy.status = CopyStatus.LOST.value
                loan.status = LoanStatus.LOST.value
            elif new_status == LoanStatus.RETURNED.value:
                # equivale a "return"; también liberamos la copia
                copy = self.copy_repo.get(loan.copy_id, for_update=True)
                if not copy:
                    raise NotFoundErrorException("Copia no encontrada")
                loan.return_date = loan.return_date or datetime.now(timezone.utc)
                loan.status = LoanStatus.RETURNED.value
                if copy.status == CopyStatus.LOANED.value:
                    copy.status = CopyStatus.AVAILABLE.value
            else:
                # OPEN o LATE (ajuste manual)
                loan.status = new_status

        return loan

    def delete(self, loan_id: UUID) -> None:
        loan = self.loan_repo.get(loan_id, for_update=True)
        if not loan:
            raise NotFoundErrorException("Préstamo no encontrado")
        # si está abierto, también liberamos la copia
        if loan.status in (LoanStatus.OPEN.value, LoanStatus.LATE.value):
            copy = self.copy_repo.get(loan.copy_id, for_update=True)
            if copy and copy.status == CopyStatus.LOANED.value:
                copy.status = CopyStatus.AVAILABLE.value
        self.loan_repo.delete(loan)

    def _parse_status(self, status: Optional[str | LoanStatus]) -> Optional[str]:
        if status is None:
            return None
        if isinstance(status, LoanStatus):
            return status.value
        try:
            return LoanStatus(status).value
        except ValueError as e:
            raise AppException("status inválido") from e

    def _ensure_member_exists(self, member_id: UUID) -> None:
        if not self.member_repo.get(member_id):
            raise NotFoundErrorException("Miembro no encontrado")

    def _ensure_copy_available(self, copy_id: UUID) -> Copy:
        # Lock de la fila que vamos a modificar
        copy = self.copy_repo.get(copy_id, for_update=True)
        if not copy:
            raise NotFoundErrorException("Copia no encontrada")
        if copy.status != CopyStatus.AVAILABLE.value:
            raise AppException("La copia no está disponible")
        return copy

    def _ensure_no_open_loan_for_copy(self, copy_id: UUID) -> None:
        exists_open = self.loan_repo.exists(filters=[Loan.copy_id == copy_id, Loan.status == LoanStatus.OPEN.value])
        if exists_open:
            raise DuplicatedErrorException("Ya existe un préstamo abierto para esta copia")