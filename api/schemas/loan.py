from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel

from api.schemas.common import BaseRead
from domain.enums.loan_status import LoanStatus

class LoanCreate(SQLModel):
    copy_id: uuid.UUID
    member_id: uuid.UUID
    due_date: datetime

class LoanUpdate(SQLModel):
    due_date: Optional[datetime] = None
    status: Optional[LoanStatus] = None

class LoanReturn(SQLModel):
    return_date: Optional[datetime] = None

class LoanRead(BaseRead):
    copy_id: uuid.UUID
    member_id: uuid.UUID
    due_date: datetime
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    status: LoanStatus = LoanStatus.OPEN