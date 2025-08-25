from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Column, Field, Relationship, String
from domain.entities.base.base_entity import BaseEntity

if TYPE_CHECKING:
    from domain.entities.catalog.book import Book

class Publisher(BaseEntity, table=True):
    __tablename__ = "publisher"
    name: str = Field(sa_column=Column("name", String(200), nullable=False, unique=True, index=True))
    website: Optional[str] = Field(default=None, sa_column=Column("website", String(300)))
    books: List["Book"] = Relationship(back_populates="publisher")