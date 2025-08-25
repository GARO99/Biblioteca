from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Column, Field, Relationship, String
from domain.entities.base.base_entity import BaseEntity

if TYPE_CHECKING:
    from domain.entities.users_traffic.fine import Fine
    from domain.entities.users_traffic.hold import Hold
    from domain.entities.users_traffic.loan import Loan


class Member(BaseEntity, table=True):
    __tablename__ = "member"
    full_name: str = Field(sa_column=Column("full_name", String(200), nullable=False, index=True))
    email: Optional[str] = Field(default=None, sa_column=Column("email", String(200), unique=True, index=True))
    phone: Optional[str] = Field(default=None, sa_column=Column("phone", String(50)))
    active: bool = Field(default=True, nullable=False)

    loans: List["Loan"] = Relationship(back_populates="member")
    holds: List["Hold"] = Relationship(back_populates="member")
    fines: List["Fine"] = Relationship(back_populates="member")