from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlmodel import Column, Field, Relationship, String
from domain.entities.base.base_entity import BaseEntity
from domain.entities.catalog.book import Book
from domain.entities.inventory.copy import Copy
from domain.entities.users_traffic.member import Member
from domain.enums.hold_status import HoldStatus


class Hold(BaseEntity, table=True):
    """
    Reserva por libro (no por copia específica).
    Cuando se cumple, puedes registrar qué copy se asignó con fulfilled_copy_id (opcional).
    """
    __tablename__ = "hold"
    book_id: uuid.UUID = Field(foreign_key="book.id", nullable=False, index=True)
    member_id: uuid.UUID = Field(foreign_key="member.id", nullable=False, index=True)
    placed_at: datetime = Field(default_factory=datetime.now(timezone.utc), nullable=False)
    status: str = Field(default=HoldStatus.ACTIVE, sa_column=Column("status", String(20), nullable=False))
    fulfilled_copy_id: Optional[uuid.UUID] = Field(default=None, foreign_key="copy.id")

    book: Book = Relationship()
    member: Member = Relationship(back_populates="holds")
    fulfilled_copy: Optional[Copy] = Relationship()