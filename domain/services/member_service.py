from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_

from domain.uow.unit_of_work import UnitOfWork
from domain.repositories.base_repository import BaseRepository
from domain.entities.users_traffic.member import Member
from utils.exceptions.not_found_error_exception import NotFoundErrorException
from utils.exceptions.duplicated_error_exception import DuplicatedErrorException


class MemberService:
    """Casos de uso de miembros."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.repo = BaseRepository[Member](Member, uow.session)

    def create(self, *, full_name: str, email: Optional[str], phone: Optional[str], active: bool) -> Member:
        if email and self._email_exists_ci(email):
            raise DuplicatedErrorException("El email ya existe")
        member = Member(full_name=full_name, email=email, phone=phone, active=active)
        self.repo.add(member)
        return member  # commit via UoW

    def list(self, *, q: Optional[str], skip: int, limit: int) -> list[Member]:
        filters = []
        if q:
            like = f"%{q}%"
            filters.append(or_(Member.full_name.like(like), Member.email.like(like)))
        return self.repo.list(filters=filters, offset=skip, limit=limit)

    def get(self, member_id: UUID) -> Member:
        member = self.repo.get(member_id)
        if not member:
            raise NotFoundErrorException("Miembro no encontrado")
        return member

    def update(
        self,
        member_id: UUID,
        *,
        full_name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        active: Optional[bool],
    ) -> Member:
        member = self.repo.get(member_id, for_update=True)
        if not member:
            raise NotFoundErrorException("Miembro no encontrado")

        if email is not None and email != getattr(member, "email", None):
            if email and self._email_exists_ci(email):
                raise DuplicatedErrorException("El email ya existe")
            member.email = email

        if full_name is not None:
            member.full_name = full_name
        if phone is not None:
            member.phone = phone
        if active is not None:
            member.active = active

        return member

    def delete(self, member_id: UUID) -> None:
        member = self.repo.get(member_id, for_update=True)
        if not member:
            raise NotFoundErrorException("Miembro no encontrado")
        self.repo.delete(member)

    def _email_exists_ci(self, email: str) -> bool:
        if not email:
            return False
        return self.repo.exists(filters=[func.lower(Member.email) == email.lower()])