from typing import TYPE_CHECKING, List, Optional
import uuid

from sqlmodel import Column, Field, Relationship, String
from domain.entities.base.base_entity import BaseEntity
from domain.enums.copy_status import CopyStatus
from domain.entities.catalog.book import Book

if TYPE_CHECKING:
    from domain.entities.users_traffic.loan import Loan


class Copy(BaseEntity, table=True):
    __tablename__ = "copy"
    book_id: uuid.UUID = Field(foreign_key="book.id", nullable=False, index=True)
    inventory_code: str = Field(sa_column=Column("inventory_code", String(100), nullable=False, unique=True, index=True))
    status: str = Field(default=CopyStatus.AVAILABLE, sa_column=Column("status", String(20), nullable=False))
    location: Optional[str] = Field(default=None, sa_column=Column("location", String(100)))

    book: Book = Relationship(back_populates="copies")
    loans: List["Loan"] = Relationship(back_populates="copy")