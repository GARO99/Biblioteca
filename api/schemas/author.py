from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel

from api.schemas.common import BaseRead

class AuthorBase(SQLModel):
    full_name: str
    bio: Optional[str] = None

class AuthorCreate(AuthorBase): ...
class AuthorUpdate(SQLModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None

class AuthorRead(AuthorBase, BaseRead): ...
