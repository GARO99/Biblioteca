from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, Literal
from sqlmodel import SQLModel

from api.schemas.common import BaseRead
from domain.enums.hold_status import HoldStatus

class HoldCreate(SQLModel):
    book_id: uuid.UUID
    member_id: uuid.UUID

class HoldFulfill(SQLModel):
    copy_id: uuid.UUID

class HoldRead(BaseRead):
    book_id: uuid.UUID
    member_id: uuid.UUID
    status: HoldStatus = HoldStatus.ACTIVE
    placed_at: Optional[datetime] = None
    fulfilled_copy_id: Optional[uuid.UUID] = None