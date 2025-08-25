from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel

from api.schemas.common import BaseRead

class MemberBase(SQLModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    active: bool = True

class MemberCreate(MemberBase): ...
class MemberUpdate(SQLModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    active: Optional[bool] = None

class MemberRead(MemberBase, BaseRead): ...