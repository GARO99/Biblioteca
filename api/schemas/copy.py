import uuid
from sqlmodel import SQLModel

from api.schemas.common import BaseRead
from domain.enums.copy_status import CopyStatus

class CopyBase(SQLModel):
    book_id: uuid.UUID
    inventory_code: str
    status: CopyStatus = CopyStatus.AVAILABLE
    location: str | None = None

class CopyCreate(CopyBase): ...
class CopyUpdate(SQLModel):
    inventory_code: str | None = None
    status: CopyStatus | None = None
    location: str | None = None

class CopyRead(CopyBase, BaseRead): ...