from __future__ import annotations
from pydantic import BaseModel, EmailStr
from domain.enums.user_role import UserRole
import uuid

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    role: UserRole

class SignInResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeRead(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: UserRole
    active: bool

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.EMPLOYEE

class UserRead(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: UserRole
    active: bool
