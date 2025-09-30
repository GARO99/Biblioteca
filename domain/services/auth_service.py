from __future__ import annotations

from domain.uow.unit_of_work import UnitOfWork
from domain.entities.security.user import User
from domain.enums.user_role import UserRole
from domain.repositories.user_repository import UserRepository
from domain.security.passwords import hash_password, verify_password
from domain.security.jwt_tokens import create_access_token
from utils.exceptions.duplicated_error_exception import DuplicatedErrorException
from utils.exceptions.not_found_error_exception import NotFoundErrorException
from utils.exceptions.app_exception import AppException

class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.repo = UserRepository(uow.session)

    def signup(self, *, full_name: str, email: str, password: str, role: UserRole) -> User:
        if self.repo.find_by_email_ci(email):
            raise DuplicatedErrorException("Email ya registrado")
        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role=role.value,
            active=True,
        )
        self.repo.add(user)
        return user

    def authenticate(self, *, email: str, password: str) -> str:
        user = self.repo.find_by_email_ci(email)
        if not user or not user.active:
            raise NotFoundErrorException("Credenciales inválidas")
        if not verify_password(password, user.password_hash):
            raise AppException("Credenciales inválidas")
        token = create_access_token(sub=str(user.id), role=user.role)
        return token
