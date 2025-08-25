from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel

from api.schemas.common import BaseRead

class PublisherBase(SQLModel):
    name: str
    website: Optional[str] = None

class PublisherCreate(PublisherBase): ...
class PublisherUpdate(SQLModel):
    name: Optional[str] = None
    website: Optional[str] = None

class PublisherRead(PublisherBase, BaseRead): ...