from __future__ import annotations
import uuid
from typing import Optional, List
from sqlmodel import SQLModel

from api.schemas.common import BaseRead

class BookBase(SQLModel):
    title: str
    isbn_13: Optional[str] = None
    language: Optional[str] = None
    published_year: Optional[int] = None
    publisher_id: Optional[uuid.UUID] = None

class BookCreate(BookBase):
    author_ids: Optional[List[uuid.UUID]] = None
    genre_ids: Optional[List[uuid.UUID]] = None

class BookUpdate(SQLModel):
    title: Optional[str] = None
    isbn_13: Optional[str] = None
    language: Optional[str] = None
    published_year: Optional[int] = None
    publisher_id: Optional[uuid.UUID] = None
    author_ids: Optional[List[uuid.UUID]] = None
    genre_ids: Optional[List[uuid.UUID]] = None

class BookRead(BookBase, BaseRead):
    author_ids: Optional[List[uuid.UUID]] = None
    genre_ids: Optional[List[uuid.UUID]] = None