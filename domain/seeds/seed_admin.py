from __future__ import annotations
import os
from sqlalchemy import select, func
from domain.uow.unit_of_work import UnitOfWorkFactory
from domain.repositories.user_repository import UserRepository
from domain.entities.security.user import User
from domain.enums.user_role import UserRole
from domain.security.passwords import hash_password

def seed_default_admin(uow_factory: UnitOfWorkFactory) -> None:
    """
    Inserta un usuario ADMIN por defecto si no existe ninguno (idempotente).
    Lee ADMIN_FULL_NAME, ADMIN_EMAIL, ADMIN_PASSWORD del entorno.
    """
    full_name = os.getenv("ADMIN_FULL_NAME", "Administrador")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not email or not password:
        # No “rompas” el arranque si no hay credenciales; simplemente no seedear
        return

    with uow_factory() as uow:
        repo = UserRepository(uow.session)

        # ¿Existe algún admin activo?
        stmt = select(func.count()).select_from(User).where(
            User.role == UserRole.ADMIN.value,
            User.active == True,  # noqa
        )
        has_admin = uow.session.execute(stmt).scalar_one() > 0
        if has_admin:
            return

        # Si no hay admin: o bien crear con los valores del .env.
        if repo.find_by_email_ci(email):
            # Si ese email ya existe pero no hay admin, no pisamos nada; salimos.
            # (Si quieres, podrías elevar un warning/log.)
            return

        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN.value,
            active=True,
        )
        repo.add(user)
        # commit lo hace el __exit__ del UoW
