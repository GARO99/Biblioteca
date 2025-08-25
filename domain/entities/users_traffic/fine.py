from datetime import datetime
from typing import Optional
import uuid

from sqlmodel import Column, Field, Relationship, String
from domain.entities.base.base_entity import BaseEntity
from domain.entities.users_traffic.member import Member


class Fine(BaseEntity, table=True):
    __tablename__ = "fine"
    member_id: uuid.UUID = Field(foreign_key="member.id", nullable=False, index=True)
    loan_id: Optional[uuid.UUID] = Field(default=None, foreign_key="loan.id")
    amount_cents: int = Field(nullable=False)
    reason: Optional[str] = Field(default=None, sa_column=Column("reason", String(300)))
    paid: bool = Field(default=False, nullable=False)
    paid_at: Optional[datetime] = Field(default=None)

    member: Member = Relationship(back_populates="fines")