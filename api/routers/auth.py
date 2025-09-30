from __future__ import annotations
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from api.schemas.auth import UserCreate, UserRead, SignInResponse, MeRead
from api.deps import get_uow
from domain.uow.unit_of_work import UnitOfWork
from domain.services.auth_service import AuthService
from api.security.deps import get_current_user, require_admin

router = APIRouter()

@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def signup(payload: UserCreate, uow: UnitOfWork = Depends(get_uow)):
    """Crear usuario (solo ADMIN)."""
    svc = AuthService(uow)
    user = svc.signup(full_name=payload.full_name, email=payload.email, password=payload.password, role=payload.role)
    return user

@router.post("/signin", response_model=SignInResponse)
def signin(form: OAuth2PasswordRequestForm = Depends(), uow: UnitOfWork = Depends(get_uow)):
    """
    Login con OAuth2 Password Flow.
    Envia `username` (email) y `password` como form-data. :contentReference[oaicite:8]{index=8}
    """
    svc = AuthService(uow)
    token = svc.authenticate(email=form.username, password=form.password)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=MeRead)
def me(user = Depends(get_current_user)):
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "active": user.active,
    }
