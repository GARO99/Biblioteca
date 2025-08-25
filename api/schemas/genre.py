from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel

from api.schemas.common import BaseRead

class GenreBase(SQLModel):
    name: str
    description: Optional[str] = None

class GenreCreate(GenreBase): ...
class GenreUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None

class GenreRead(GenreBase, BaseRead): ...