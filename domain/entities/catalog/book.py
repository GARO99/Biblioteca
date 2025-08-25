from typing import TYPE_CHECKING, List, Optional
import uuid
from sqlmodel import Column, Field, Relationship, String
from domain.entities.base.base_entity import BaseEntity
from domain.entities.catalog.book_author_link import BookAuthorLink
from domain.entities.catalog.book_genre_link import BookGenreLink
from domain.entities.catalog.publisher import Publisher

if TYPE_CHECKING:
    from domain.entities.catalog.author import Author
    from domain.entities.catalog.genre import Genre
    from domain.entities.inventory.copy import Copy

class Book(BaseEntity, table=True):
    __tablename__ = "book"
    title: str = Field(sa_column=Column("title", String(300), nullable=False, index=True))
    isbn_13: Optional[str] = Field(default=None, sa_column=Column("isbn_13", String(13), unique=True, index=True))
    language: Optional[str] = Field(default=None, sa_column=Column("language", String(50)))
    published_year: Optional[int] = Field(default=None)
    publisher_id: Optional[uuid.UUID] = Field(default=None, foreign_key="publisher.id")

    publisher: Optional[Publisher] = Relationship(back_populates="books")
    authors: List["Author"] = Relationship(back_populates="books", link_model=BookAuthorLink)
    genres: List["Genre"] = Relationship(back_populates="books", link_model=BookGenreLink)
    copies: List["Copy"] = Relationship(back_populates="book")