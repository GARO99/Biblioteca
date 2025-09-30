from fastapi import Depends, HTTPException, status
from uuid import UUID
from domain.uow.unit_of_work import UnitOfWork
from api.deps import get_uow
from core.project_config import ProjectConfig
from domain.security.jwt_tokens import decode_token
from domain.repositories.user_repository import UserRepository
from domain.enums.user_role import UserRole

oauth2_scheme = ProjectConfig.OAUTH2_SCHEME_EMPLOYEED()

def get_current_user(uow: UnitOfWork = Depends(get_uow), token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("No sub")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    user = UserRepository(uow.session).get(UUID(user_id))
    if not user or not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inactivo o no encontrado")
    return user

def require_employee(user=Depends(get_current_user)):
    if user.role not in (UserRole.EMPLOYEE.value, UserRole.ADMIN.value):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    return user

def require_admin(user=Depends(get_current_user)):
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Solo administradores")
    return user
