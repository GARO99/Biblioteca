from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlmodel import Column, Field, Relationship, String
from domain.entities.base.base_entity import BaseEntity
from domain.entities.inventory.copy import Copy
from domain.entities.users_traffic.member import Member
from domain.enums.loan_status import LoanStatus


class Loan(BaseEntity, table=True):
    __tablename__ = "loan"
    copy_id: uuid.UUID = Field(foreign_key="copy.id", nullable=False, index=True)
    member_id: uuid.UUID = Field(foreign_key="member.id", nullable=False, index=True)
    loan_date: datetime = Field(default_factory=datetime.now(timezone.utc), nullable=False)
    due_date: datetime = Field(nullable=False)
    return_date: Optional[datetime] = Field(default=None)
    status: str = Field(default=LoanStatus.OPEN, sa_column=Column("status", String(20), nullable=False))

    copy: Copy = Relationship(back_populates="loans")
    member: Member = Relationship(back_populates="loans")
