from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Column, Field, Relationship, String

from domain.entities.base.base_entity import BaseEntity
from domain.entities.catalog.book_author_link import BookAuthorLink

if TYPE_CHECKING:
    from domain.entities.catalog.book import Book


class Author(BaseEntity, table=True):
    __tablename__ = "author"
    full_name: str = Field(sa_column=Column("full_name", String(200), nullable=False, index=True))
    bio: Optional[str] = Field(default=None, sa_column=Column("bio", String(2000)))
    books: List["Book"] = Relationship(back_populates="authors", link_model=BookAuthorLink)