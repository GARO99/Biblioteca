from __future__ import annotations
from sqlmodel import Field, Column, String
from domain.entities.base.base_entity import BaseEntity
from domain.enums.user_role import UserRole

class User(BaseEntity, table=True):
    __tablename__ = "user"
    full_name: str = Field(sa_column=Column("full_name", String(200), nullable=False))
    email: str = Field(sa_column=Column("email", String(200), nullable=False, unique=True, index=True))
    password_hash: str = Field(sa_column=Column("password_hash", String(255), nullable=False))
    role: str = Field(sa_column=Column("role", String(20), nullable=False, default=UserRole.EMPLOYEE.value))
    active: bool = Field(default=True, nullable=False)
