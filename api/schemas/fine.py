from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from .common import BaseRead


class FineCreate(SQLModel):
    member_id: uuid.UUID
    amount_cents: int
    loan_id: Optional[uuid.UUID] = None
    reason: Optional[str] = None


class FineUpdate(SQLModel):
    amount_cents: Optional[int] = None
    reason: Optional[str] = None
    paid: Optional[bool] = None
    paid_at: Optional[datetime] = None
    loan_id: Optional[uuid.UUID] = None


class FineRead(BaseRead):
    member_id: uuid.UUID
    loan_id: Optional[uuid.UUID] = None
    amount_cents: int
    reason: Optional[str] = None
    paid: bool
    paid_at: Optional[datetime] = None


class FinePay(SQLModel):
    paid_at: Optional[datetime] = None