from __future__ import annotations
import uuid
from pydantic import ConfigDict
from sqlmodel import SQLModel

class BaseRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID