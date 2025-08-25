from typing import List, Optional
from sqlmodel import Column, Field, Relationship, String
from domain.entities.base.base_entity import BaseEntity
from domain.entities.catalog.book import Book
from domain.entities.catalog.book_genre_link import BookGenreLink


class Genre(BaseEntity, table=True):
    __tablename__ = "genre"
    name: str = Field(sa_column=Column("name", String(100), nullable=False, unique=True, index=True))
    description: Optional[str] = Field(default=None, sa_column=Column("description", String(500)))
    books: List["Book"] = Relationship(back_populates="genres", link_model=BookGenreLink)